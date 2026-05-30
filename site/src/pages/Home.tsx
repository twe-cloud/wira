import FAQ from "@/components/FAQ";
import Footer from "@/components/Footer";
import Founder from "@/components/Founder";
import Hero from "@/components/Hero";
import HowItWorks from "@/components/HowItWorks";
import Nav from "@/components/Nav";
import Pillars from "@/components/Pillars";
import Pricing from "@/components/Pricing";
import SocialProof from "@/components/SocialProof";
import VoiceToggle from "@/components/VoiceToggle";

export default function Home() {
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <SocialProof />
        <Pillars />
        <HowItWorks />
        <VoiceToggle />
        <Founder />
        <Pricing />
        <FAQ />
      </main>
      <Footer />
    </>
  );
}
