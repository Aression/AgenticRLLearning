import { Atlas } from "@/components/atlas";
import { getGraph, getNotes, getSources } from "@/lib/content";

export default function Home() {
  return <Atlas notes={getNotes()} sources={getSources()} graph={getGraph()} />;
}
