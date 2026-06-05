import { Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import Learn from "./pages/Learn";
import NerdStuff from "./pages/NerdStuff";
import NotFound from "./pages/NotFound";
import Onboarding from "./pages/Onboarding";
import Privacy from "./pages/Privacy";
import Success from "./pages/Success";
import Terms from "./pages/Terms";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/learn" element={<Learn />} />
      <Route path="/nerd-stuff" element={<NerdStuff />} />
      <Route path="/success" element={<Success />} />
      <Route path="/onboarding" element={<Onboarding />} />
      <Route path="/privacy" element={<Privacy />} />
      <Route path="/terms" element={<Terms />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
