import { Map } from "@/components/map";
import Head from "next/head";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "ITMS",
}

export default function Home() {
  return(
    <div>
      <Map />
    </div>
  )
}