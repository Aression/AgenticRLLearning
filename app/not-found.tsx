import Link from "next/link";
export default function NotFound() { return <main id="main-content" className="not-found"><p className="mono cyan">404 / NOTE NOT FOUND</p><h1>这篇笔记不存在</h1><p>链接可能已变更，回到知识地图重新查找。</p><Link className="command primary" href="/">返回知识地图</Link></main>; }
