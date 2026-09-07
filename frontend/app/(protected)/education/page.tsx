import { EducationList } from "@/components/EducationList";

export default function EducationPage() {
  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-2">Bilgi Merkezi</h1>
      <p className="text-gray-600 mb-8">Finansal okuryazarlığınızı geliştirin ve Karar Motorumuzun arkasındaki matematiği keşfedin.</p>
      
      <EducationList />
    </div>
  );
}
