import { Atlas } from "@/components/atlas";
import { getGraph, getNotes, getRadar, getSources } from "@/lib/content";

export default function Home() {
  return <Atlas notes={getNotes()} sources={getSources()} graph={getGraph()} radar={getRadar()} />;
}
