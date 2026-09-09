import re

with open('frontend/app/(protected)/settings/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

replacement = '''  const [riskTolerance, setRiskTolerance] = useState("MEDIUM");
  const [explanationLevel, setExplanationLevel] = useState("PRO");
  const [saved, setSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    fetchApi("/api/v1/users/profile").then((profile: any) => {
      if (profile?.risk_tolerance) {
        setRiskTolerance(profile.risk_tolerance);
      }
    }).catch(console.error);

    const storedLevel = localStorage.getItem('bt_explanation_level');
    if (storedLevel) setExplanationLevel(storedLevel);
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await fetchApi("/api/v1/users/profile", {
        method: "PUT",
        body: JSON.stringify({
          risk_tolerance: riskTolerance,
        })
      });
      localStorage.setItem('bt_explanation_level', explanationLevel);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e) {
      console.error(e);
      alert("Hata oluþtu.");
    } finally {
      setIsSaving(false);
    }
  };'''

new_content = re.sub(
    r'  const \[riskTolerance.*?setTimeout\(\(\) => setSaved\(false\), 2000\);\n  };',
    replacement,
    content,
    flags=re.DOTALL
)

with open('frontend/app/(protected)/settings/page.tsx', 'w', encoding='utf-8') as f:
    f.write(new_content)
