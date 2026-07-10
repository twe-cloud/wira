import AgentPromise from "@/components/AgentPromise";
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
import { PRODUCT } from "@/lib/brand";
import { faqSchema, Seo, softwareApplicationSchema, websiteSchema } from "@/lib/seo";

export default function Home() {
  return (
    <>
      <Seo
        title="Wira | WhatsApp AI Agent for Your Computer"
        description={PRODUCT.description}
        path="/"
        structuredData={[websiteSchema(), softwareApplicationSchema(), faqSchema()]}
      />
      <Nav />
      <main>
        <Hero />
        <SocialProof />
        <Pillars />
        <HowItWorks />
        <AgentPromise />
        <VoiceToggle />
        <Founder />
        <Pricing />
        <FAQ />
      </main>
      <Footer />
    </>
  );
}
