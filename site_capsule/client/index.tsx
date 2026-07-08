import { useEffect } from "preact/hooks";

export function App() {
  useEffect(() => {
    window.location.replace("/index");
  }, []);

  return (
    <main className="min-h-screen bg-black px-6 py-10 text-white">
      <a className="text-neutral-200 underline" href="/index">
        JouleWise site
      </a>
    </main>
  );
}
