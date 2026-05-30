import { Link } from "react-router-dom";
import Footer from "@/components/Footer";
import Nav from "@/components/Nav";

export default function NotFound() {
  return (
    <>
      <Nav />
      <main className="container-narrow py-32 text-center">
        <p className="font-display text-7xl text-accent">404</p>
        <h1 className="mt-4 text-3xl">Not here.</h1>
        <p className="mt-3 text-ink-muted">
          That page doesn't exist. The good news: the assistant probably would
          have replied to it anyway.
        </p>
        <Link to="/" className="btn-primary mt-8">
          Take me home
        </Link>
      </main>
      <Footer />
    </>
  );
}
