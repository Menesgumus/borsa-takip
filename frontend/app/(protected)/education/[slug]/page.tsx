import EducationDetailClient from "./EducationDetailClient";

export default async function EducationDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return <EducationDetailClient slug={slug} />;
}
