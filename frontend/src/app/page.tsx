"use client";

import { useEffect, useMemo, useState } from "react";

type User = {
  id: number;
  email: string;
  created_at: string;
};

type Post = {
  id: number;
  title: string;
  content: string;
  category: string;
  published: boolean;
  created_at: string;
  user_id: number;
  owner: User;
};

type PostWithVotes = {
  Post: Post;
  vote_count: number;
};

const apiBase =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

function decodeTokenSub(token: string): number | null {
  try {
    const payload = token.split(".")[1];
    if (!payload) return null;
    const base64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    const padded = base64.padEnd(Math.ceil(base64.length / 4) * 4, "=");
    const json = atob(padded);
    const data = JSON.parse(json) as { sub?: string };
    if (!data.sub) return null;
    return Number(data.sub);
  } catch {
    return null;
  }
}

async function apiFetch(path: string, options: RequestInit = {}) {
  const response = await fetch(`${apiBase}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Request failed");
  }
  if (response.status === 204) return null;
  return response.json();
}

export default function Home() {
  const [token, setToken] = useState<string | null>(null);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [posts, setPosts] = useState<PostWithVotes[]>([]);
  const [authLoading, setAuthLoading] = useState(false);
  const [loadingPosts, setLoadingPosts] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [registerEmail, setRegisterEmail] = useState("");
  const [registerPassword, setRegisterPassword] = useState("");

  const [postTitle, setPostTitle] = useState("");
  const [postContent, setPostContent] = useState("");
  const [postCategory, setPostCategory] = useState("Generic");
  const [postPublished, setPostPublished] = useState(true);
  const [editingPostId, setEditingPostId] = useState<number | null>(null);

  const [votingPostId, setVotingPostId] = useState<number | null>(null);

  const [profileEmail, setProfileEmail] = useState("");
  const [profilePassword, setProfilePassword] = useState("");

  const authHeaders = useMemo<HeadersInit>(() => {
    if (!token) return {};
    return { Authorization: `Bearer ${token}` };
  }, [token]);

  useEffect(() => {
    const saved = localStorage.getItem("access_token");
    if (saved) setToken(saved);
  }, []);

  useEffect(() => {
    if (!token) {
      setCurrentUser(null);
      setPosts([]);
      return;
    }
    const userId = decodeTokenSub(token);
    if (!userId) {
      handleLogout();
      return;
    }
    void fetchCurrentUser(userId, token);
    void fetchPosts(token);
  }, [token]);

  async function fetchCurrentUser(userId: number, accessToken: string) {
    try {
      const data = await apiFetch(`/users/${userId}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      setCurrentUser(data as User);
      setProfileEmail((data as User).email);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load user");
    }
  }

  async function fetchPosts(accessToken: string) {
    setLoadingPosts(true);
    setError(null);
    try {
      const data = await apiFetch("/posts?limit=50", {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      setPosts(data as PostWithVotes[]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load posts");
    } finally {
      setLoadingPosts(false);
    }
  }

  async function handleLoginWithCredentials(email: string, password: string) {
    setAuthLoading(true);
    setError(null);
    setMessage(null);
    try {
      const body = new URLSearchParams({
        username: email,
        password,
      });
      const response = await fetch(`${apiBase}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });
      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || "Login failed");
      }
      const data = (await response.json()) as { access_token: string };
      localStorage.setItem("access_token", data.access_token);
      setToken(data.access_token);
      setLoginPassword("");
      setMessage("Logged in successfully");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setAuthLoading(false);
    }
  }

  async function handleLogin() {
    if (!loginEmail || !loginPassword) {
      setError("Please enter email and password.");
      return;
    }
    await handleLoginWithCredentials(loginEmail, loginPassword);
  }

  async function handleRegister() {
    setAuthLoading(true);
    setError(null);
    setMessage(null);
    try {
      await apiFetch("/users", {
        method: "POST",
        body: JSON.stringify({
          email: registerEmail,
          password: registerPassword,
        }),
      });
      setMessage("Account created. Logging you in...");
      setLoginEmail(registerEmail);
      setLoginPassword("");
      await handleLoginWithCredentials(registerEmail, registerPassword);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setAuthLoading(false);
    }
  }

  async function handleCreateOrUpdatePost() {
    if (!token) return;
    setError(null);
    setMessage(null);
    try {
      const payload = {
        title: postTitle,
        content: postContent,
        category: postCategory,
        published: postPublished,
      };
      if (editingPostId) {
        await apiFetch(`/posts/${editingPostId}`, {
          method: "PUT",
          headers: authHeaders,
          body: JSON.stringify(payload),
        });
        setMessage("Post updated");
      } else {
        await apiFetch("/posts", {
          method: "POST",
          headers: authHeaders,
          body: JSON.stringify(payload),
        });
        setMessage("Post created");
      }
      setPostTitle("");
      setPostContent("");
      setPostCategory("Generic");
      setPostPublished(true);
      setEditingPostId(null);
      await fetchPosts(token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save post");
    }
  }

  function handleEditPost(post: Post) {
    setEditingPostId(post.id);
    setPostTitle(post.title);
    setPostContent(post.content);
    setPostCategory(post.category);
    setPostPublished(post.published);
  }

  async function handleDeletePost(postId: number) {
    if (!token) return;
    setError(null);
    setMessage(null);
    try {
      await apiFetch(`/posts/${postId}`, {
        method: "DELETE",
        headers: authHeaders,
      });
      setMessage("Post deleted");
      await fetchPosts(token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete post");
    }
  }

  async function handleVote(postId: number, dir: 0 | 1) {
    if (!token) return;
    setVotingPostId(postId);
    setError(null);
    setMessage(null);
    try {
      await apiFetch("/vote", {
        method: "POST",
        headers: authHeaders,
        body: JSON.stringify({ post_id: postId, dir }),
      });
      setMessage(dir === 1 ? "Vote added" : "Vote removed");
      await fetchPosts(token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to vote");
    } finally {
      setVotingPostId(null);
    }
  }

  async function handleUpdateProfile() {
    if (!token || !currentUser) return;
    if (!profilePassword) {
      setError("Please enter a new password to update your profile.");
      return;
    }
    setError(null);
    setMessage(null);
    try {
      const data = await apiFetch(`/users/${currentUser.id}`, {
        method: "PUT",
        headers: authHeaders,
        body: JSON.stringify({
          email: profileEmail,
          password: profilePassword,
        }),
      });
      setCurrentUser(data as User);
      setProfilePassword("");
      setMessage("Profile updated");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update profile");
    }
  }

  async function handleDeleteProfile() {
    if (!token || !currentUser) return;
    setError(null);
    setMessage(null);
    try {
      await apiFetch(`/users/${currentUser.id}`, {
        method: "DELETE",
        headers: authHeaders,
      });
      handleLogout();
      setMessage("Account deleted");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete profile");
    }
  }

  function handleLogout() {
    localStorage.removeItem("access_token");
    setToken(null);
    setCurrentUser(null);
    setPosts([]);
  }

  return (
    <div className="container">
      <div className="hero">
        <div>
          <h1>Social App Control Center</h1>
          <p>Manage your account and posts with the FastAPI backend.</p>
        </div>
        <div className="actions">
          {token ? (
            <button className="btn btn-outline" onClick={handleLogout}>
              Sign out
            </button>
          ) : null}
        </div>
      </div>

      <div className="banner">
        API base: {apiBase}
      </div>

      {error ? <div className="banner" style={{ marginTop: 12 }}>
        {error}
      </div> : null}
      {message ? <div className="banner" style={{ marginTop: 12 }}>
        {message}
      </div> : null}

      {!token ? (
        <div className="grid" style={{ marginTop: 24 }}>
          <div className="card stack">
            <div className="section-title">Login</div>
            <input
              className="input"
              placeholder="Email"
              value={loginEmail}
              onChange={(e) => setLoginEmail(e.target.value)}
            />
            <input
              className="input"
              placeholder="Password"
              type="password"
              value={loginPassword}
              onChange={(e) => setLoginPassword(e.target.value)}
            />
            <button
              className="btn btn-primary"
              onClick={handleLogin}
              disabled={authLoading || !loginEmail || !loginPassword}
            >
              Sign in
            </button>
          </div>
          <div className="card stack">
            <div className="section-title">Create account</div>
            <input
              className="input"
              placeholder="Email"
              value={registerEmail}
              onChange={(e) => setRegisterEmail(e.target.value)}
            />
            <input
              className="input"
              placeholder="Password"
              type="password"
              value={registerPassword}
              onChange={(e) => setRegisterPassword(e.target.value)}
            />
            <button
              className="btn btn-success"
              onClick={handleRegister}
              disabled={authLoading || !registerEmail || !registerPassword}
            >
              Register
            </button>
          </div>
        </div>
      ) : (
        <div className="grid" style={{ marginTop: 24 }}>
          <div className="card stack">
            <div className="section-title">My profile</div>
            {currentUser ? (
              <div className="stack">
                <div className="muted">User ID: {currentUser.id}</div>
                <input
                  className="input"
                  value={profileEmail}
                  onChange={(e) => setProfileEmail(e.target.value)}
                />
                <input
                  className="input"
                  type="password"
                  placeholder="New password"
                  value={profilePassword}
                  onChange={(e) => setProfilePassword(e.target.value)}
                />
                <div className="actions">
                  <button
                    className="btn btn-primary"
                    onClick={handleUpdateProfile}
                  >
                    Update profile
                  </button>
                  <button
                    className="btn btn-danger"
                    onClick={handleDeleteProfile}
                  >
                    Delete account
                  </button>
                </div>
              </div>
            ) : (
              <div className="muted">Loading profile...</div>
            )}
          </div>

          <div className="card stack">
            <div className="section-title">
              {editingPostId ? "Edit post" : "Create post"}
            </div>
            <input
              className="input"
              placeholder="Title"
              value={postTitle}
              onChange={(e) => setPostTitle(e.target.value)}
            />
            <textarea
              className="textarea"
              placeholder="Content"
              value={postContent}
              onChange={(e) => setPostContent(e.target.value)}
            />
            <input
              className="input"
              placeholder="Category"
              value={postCategory}
              onChange={(e) => setPostCategory(e.target.value)}
            />
            <div className="row">
              <label className="muted">
                <input
                  type="checkbox"
                  checked={postPublished}
                  onChange={(e) => setPostPublished(e.target.checked)}
                />{" "}
                Published
              </label>
              {editingPostId ? (
                <button
                  className="btn btn-outline"
                  onClick={() => {
                    setEditingPostId(null);
                    setPostTitle("");
                    setPostContent("");
                    setPostCategory("Generic");
                    setPostPublished(true);
                  }}
                >
                  Cancel
                </button>
              ) : null}
            </div>
            <button
              className="btn btn-success"
              onClick={handleCreateOrUpdatePost}
              disabled={!postTitle || !postContent}
            >
              {editingPostId ? "Save changes" : "Publish post"}
            </button>
          </div>
        </div>
      )}

      {token ? (
        <div style={{ marginTop: 32 }}>
          <div className="section-title">Latest posts</div>
          {loadingPosts ? (
            <div className="muted">Loading posts...</div>
          ) : posts.length === 0 ? (
            <div className="muted">No posts found.</div>
          ) : (
            <div className="grid">
              {posts.map(({ Post: post, vote_count }) => (
                <div key={post.id} className="card post-card stack">
                  <div className="row" style={{ justifyContent: "space-between" }}>
                    <h3>{post.title}</h3>
                    <span className="tag">Votes: {vote_count}</span>
                  </div>
                  <div className="muted">{post.category}</div>
                  <p>{post.content}</p>
                  <div className="row" style={{ justifyContent: "space-between" }}>
                    <span className="muted">
                      By {post.owner?.email ?? "Unknown"}
                    </span>
                    <span className="muted">
                      {new Date(post.created_at).toLocaleString()}
                    </span>
                  </div>
                  <div className="divider" />
                  <div className="actions">
                    <button
                      className="btn btn-primary"
                      onClick={() => handleVote(post.id, 1)}
                      disabled={votingPostId === post.id}
                    >
                      Upvote
                    </button>
                    <button
                      className="btn btn-outline"
                      onClick={() => handleVote(post.id, 0)}
                      disabled={votingPostId === post.id}
                    >
                      Remove vote
                    </button>
                    {currentUser?.id === post.user_id ? (
                      <>
                        <button
                          className="btn btn-outline"
                          onClick={() => handleEditPost(post)}
                        >
                          Edit
                        </button>
                        <button
                          className="btn btn-danger"
                          onClick={() => handleDeletePost(post.id)}
                        >
                          Delete
                        </button>
                      </>
                    ) : (
                      <span className="muted">Read-only</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}
