export default function RecentPosts({ posts }) {
  return (
    <div>
      <h3>Recent Posts</h3>
      <ul>
        {posts.map((post) => (
          <li key={post.post_id} style={{ marginBottom: "10px" }}>
            <b>{post.sentiment}</b> — {post.content.slice(0, 80)}...
          </li>
        ))}
      </ul>
    </div>
  );
}
