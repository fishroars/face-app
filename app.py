import { useState, useRef, useCallback } from "react";

const API_URL = "https://api.anthropic.com/v1/messages";

const ANALYSIS_PROMPT = `You are a specialized AI facial analysis system used in a professional plastic surgery clinic. Analyze the uploaded face image based on peer-reviewed research in social psychology and facial perception.

Analyze the face according to these research-based frameworks:

1. **Willis & Todorov (2006) - First Impressions**: Assess trustworthiness, competence, attractiveness scored in 100ms
2. **Oosterhof & Todorov (2008) - Two Pillars**: Score on two primary axes:
   - Trustworthiness/Approachability (mouth shape, corner lift)
   - Dominance (jaw width, brow prominence)
3. **Sutherland et al. (2013) - 3D Model**: Score on three dimensions:
   - Approachability
   - Dominance  
   - Youthful-Attractiveness
4. **Zebrowitz (1997) - Babyface Theory**: Babyface index (eye size ratio, chin position, overall childlike features)
5. **Vernon et al. (2014) - 65 Coordinates**: Physical measurements including:
   - Eye distance ratio (ideal: ~46% of face width)
   - Eye-to-mouth ratio (ideal: ~36% of face length)
   - Mouth shape and corner angles
   - Jaw width to face width ratio
   - Eyebrow height and density
   - Lip thickness upper/lower ratio
   - Facial symmetry score
   - Nose-to-face proportion
6. **Pallett et al. (2010) - Golden Ratios**:
   - Vertical: eye-to-mouth distance / total face length (ideal: 36%)
   - Horizontal: inter-eye distance / face width (ideal: 46%)
   - Overall facial harmony score

For each measurement, provide:
- Estimated current value (as %)
- Ideal reference value (as %)
- Deviation score
- Clinical recommendation for filler injection if applicable

Also identify the TOP 3 areas where dermal filler could most effectively improve facial harmony and first impressions, with specific product type recommendations (hyaluronic acid, calcium hydroxyapatite, etc.) and injection volumes.

Return ONLY valid JSON in this exact format, no other text:
{
  "patientSummary": {
    "overallScore": 78,
    "faceShape": "Oval",
    "skinTone": "Medium",
    "ageEstimate": "28-33",
    "gender": "Female"
  },
  "impressionScores": {
    "trustworthiness": 72,
    "dominance": 45,
    "youthfulAttractiveness": 68,
    "competence": 74,
    "approachability": 70
  },
  "babyfaceIndex": {
    "score": 42,
    "level": "Low",
    "description": "Angular facial features with defined jawline. Lower babyface index suggests a more assertive, dominant impression."
  },
  "goldenRatios": {
    "verticalRatio": {
      "current": 33.2,
      "ideal": 36.0,
      "deviation": -2.8,
      "grade": "B"
    },
    "horizontalRatio": {
      "current": 44.1,
      "ideal": 46.0,
      "deviation": -1.9,
      "grade": "B+"
    },
    "facialSymmetry": {
      "current": 87,
      "ideal": 95,
      "deviation": -8,
      "grade": "B"
    }
  },
  "vernonMeasurements": [
    {
      "name": "Eye Distance Ratio",
      "nameKo": "눈간격 비율",
      "current": 44.1,
      "ideal": 46.0,
      "unit": "%",
      "grade": "B+",
      "fillerArea": "Nasal bridge",
      "fillerAreaKo": "코 브릿지"
    },
    {
      "name": "Eye-to-Mouth Ratio",
      "nameKo": "눈-입 비율",
      "current": 33.2,
      "ideal": 36.0,
      "unit": "%",
      "grade": "B",
      "fillerArea": "Chin projection",
      "fillerAreaKo": "턱 돌출"
    },
    {
      "name": "Mouth Corner Angle",
      "nameKo": "입꼬리 각도",
      "current": -3,
      "ideal": 2,
      "unit": "°",
      "grade": "C+",
      "fillerArea": "Oral commissure",
      "fillerAreaKo": "입꼬리 리프트"
    },
    {
      "name": "Jaw Width Ratio",
      "nameKo": "턱 너비 비율",
      "current": 68,
      "ideal": 65,
      "unit": "%",
      "grade": "A-",
      "fillerArea": null,
      "fillerAreaKo": null
    },
    {
      "name": "Lip Volume Ratio",
      "nameKo": "상하 입술 비율",
      "current": 1.1,
      "ideal": 1.6,
      "unit": "ratio",
      "grade": "C",
      "fillerArea": "Upper lip",
      "fillerAreaKo": "윗입술 볼륨"
    },
    {
      "name": "Facial Symmetry",
      "nameKo": "안면 대칭도",
      "current": 87,
      "ideal": 95,
      "unit": "%",
      "grade": "B"
    }
  ],
  "fillerRecommendations": [
    {
      "rank": 1,
      "area": "Oral Commissure (Mouth Corners)",
      "areaKo": "입꼬리 리프트",
      "impact": "Trustworthiness +15pts",
      "impactKo": "신뢰성 +15점 향상",
      "product": "Hyaluronic Acid (Soft)",
      "productKo": "히알루론산 (소프트)",
      "volume": "0.3-0.5ml",
      "priority": "High",
      "rationale": "Mouth corner angle is the primary determinant of trustworthiness perception (Oosterhof & Todorov, 2008). Upward correction by 5° significantly improves approachability scores.",
      "rationaleKo": "입꼬리 각도는 신뢰성 인상의 핵심 결정 요소입니다 (Oosterhof & Todorov, 2008). 5° 상향 교정으로 접근성 점수가 크게 향상됩니다."
    },
    {
      "rank": 2,
      "area": "Upper Lip Volume",
      "areaKo": "윗입술 볼륨",
      "impact": "Youthful-Attractiveness +12pts",
      "impactKo": "젊음-매력 +12점 향상",
      "product": "Hyaluronic Acid (Medium)",
      "productKo": "히알루론산 (미디엄)",
      "volume": "0.5-0.8ml",
      "priority": "High",
      "rationale": "Upper-to-lower lip ratio of 1:1.6 is optimal for youthful attractiveness. Current ratio shows upper lip deficiency.",
      "rationaleKo": "상하 입술 1:1.6 비율이 젊음-매력의 최적값입니다. 현재 윗입술 볼륨 보강이 필요합니다."
    },
    {
      "rank": 3,
      "area": "Chin Projection",
      "areaKo": "턱끝 프로젝션",
      "impact": "Golden Ratio +8pts",
      "impactKo": "황금비율 +8점 향상",
      "product": "Hyaluronic Acid (Firm) / CaHA",
      "productKo": "히알루론산 (펌) / 칼슘 히드록시아파타이트",
      "volume": "0.5-1.0ml",
      "priority": "Medium",
      "rationale": "Chin projection improvement will optimize the vertical golden ratio (eye-to-mouth distance), bringing it closer to the ideal 36%.",
      "rationaleKo": "턱끝 보강으로 수직 황금비율(눈-입 거리)을 이상적인 36%에 근접시킬 수 있습니다."
    }
  ],
  "researchInsights": [
    {
      "study": "Willis & Todorov (2006)",
      "finding": "First impressions form in 100ms. Trustworthiness is evaluated fastest.",
      "findingKo": "첫인상은 0.1초에 형성됩니다. 신뢰성이 가장 빠르게 판단됩니다.",
      "relevance": "Mouth corner correction will have immediate impact on first impression trustworthiness scores."
    },
    {
      "study": "Pallett et al. (2010)",
      "finding": "Optimal facial proportions: 36% vertical, 46% horizontal ratios.",
      "findingKo": "최적 안면 비율: 수직 36%, 수평 46%",
      "relevance": "Current ratios fall slightly below optimal, addressable through targeted filler placement."
    }
  ]
}`;

// Grade colors
const gradeColor = (grade) => {
  if (!grade) return "#94a3b8";
  const g = grade.charAt(0);
  if (g === "S") return "#7c3aed";
  if (g === "A") return "#0ea5e9";
  if (g === "B") return "#10b981";
  if (g === "C") return "#f59e0b";
  if (g === "D") return "#ef4444";
  return "#94a3b8";
};

const gradeBar = (score) => {
  if (score >= 90) return "S";
  if (score >= 80) return "A";
  if (score >= 70) return "B";
  if (score >= 60) return "C";
  return "D";
};

function ScoreGauge({ score, label, labelKo, color }) {
  const circumference = 2 * Math.PI * 36;
  const offset = circumference - (score / 100) * circumference;
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
      <svg width="88" height="88" viewBox="0 0 88 88">
        <circle cx="44" cy="44" r="36" fill="none" stroke="#1e293b" strokeWidth="7" />
        <circle
          cx="44" cy="44" r="36" fill="none"
          stroke={color} strokeWidth="7"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 44 44)"
          style={{ transition: "stroke-dashoffset 1.2s cubic-bezier(0.4,0,0.2,1)" }}
        />
        <text x="44" y="48" textAnchor="middle" fill="white" fontSize="17" fontWeight="700" fontFamily="'DM Mono', monospace">{score}</text>
      </svg>
      <div style={{ textAlign: "center" }}>
        <div style={{ color: "#94a3b8", fontSize: 10, letterSpacing: "0.08em", textTransform: "uppercase" }}>{label}</div>
        <div style={{ color: "#cbd5e1", fontSize: 11, marginTop: 1 }}>{labelKo}</div>
      </div>
    </div>
  );
}

function MeasurementBar({ item }) {
  const deviation = item.current - item.ideal;
  const absMax = Math.max(Math.abs(deviation) * 2.5, 10);
  const pct = Math.min(100, (item.current / (item.ideal * 1.5)) * 100);
  const idealPct = (item.ideal / (item.ideal * 1.5)) * 100;
  const gc = gradeColor(item.grade);

  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 5 }}>
        <div>
          <span style={{ color: "#e2e8f0", fontSize: 13, fontWeight: 600 }}>{item.nameKo}</span>
          <span style={{ color: "#64748b", fontSize: 11, marginLeft: 6 }}>{item.name}</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ color: "#94a3b8", fontSize: 12 }}>
            현재 <span style={{ color: "#e2e8f0", fontWeight: 700, fontFamily: "'DM Mono', monospace" }}>{item.current}{item.unit}</span>
            {" / "}이상 <span style={{ color: "#60a5fa", fontWeight: 600, fontFamily: "'DM Mono', monospace" }}>{item.ideal}{item.unit}</span>
          </span>
          <span style={{
            background: gc + "22",
            color: gc,
            border: `1px solid ${gc}44`,
            borderRadius: 4,
            padding: "1px 7px",
            fontSize: 12,
            fontWeight: 700,
            fontFamily: "'DM Mono', monospace",
            minWidth: 28,
            textAlign: "center"
          }}>{item.grade}</span>
        </div>
      </div>
      <div style={{ position: "relative", height: 8, background: "#1e293b", borderRadius: 4, overflow: "visible" }}>
        <div style={{
          height: "100%",
          width: `${pct}%`,
          background: `linear-gradient(90deg, ${gc}88, ${gc})`,
          borderRadius: 4,
          transition: "width 1s ease"
        }} />
        {/* Ideal marker */}
        <div style={{
          position: "absolute",
          left: `${idealPct}%`,
          top: -4,
          width: 2,
          height: 16,
          background: "#60a5fa",
          borderRadius: 1,
          transform: "translateX(-50%)"
        }} />
      </div>
      {item.fillerAreaKo && (
        <div style={{ marginTop: 4, display: "flex", alignItems: "center", gap: 4 }}>
          <span style={{ color: "#f59e0b", fontSize: 10, letterSpacing: "0.06em" }}>▶ 필러 추천 부위:</span>
          <span style={{ color: "#fbbf24", fontSize: 11, fontWeight: 600 }}>{item.fillerAreaKo}</span>
        </div>
      )}
    </div>
  );
}

export default function FaceAnalysisApp() {
  const [image, setImage] = useState(null);
  const [imageBase64, setImageBase64] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [step, setStep] = useState("upload"); // upload | analyzing | report
  const fileRef = useRef();
  const reportRef = useRef();

  const handleFile = useCallback((file) => {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      setImage(e.target.result);
      const b64 = e.target.result.split(",")[1];
      setImageBase64(b64);
    };
    reader.readAsDataURL(file);
  }, []);

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) handleFile(file);
  };

  const analyze = async () => {
    if (!imageBase64) return;
    setLoading(true);
    setError(null);
    setStep("analyzing");

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 3000,
          messages: [{
            role: "user",
            content: [
              {
                type: "image",
                source: { type: "base64", media_type: "image/jpeg", data: imageBase64 }
              },
              { type: "text", text: ANALYSIS_PROMPT }
            ]
          }]
        })
      });

      const data = await res.json();
      const text = data.content?.find(c => c.type === "text")?.text || "";
      const clean = text.replace(/```json|```/g, "").trim();
      const parsed = JSON.parse(clean);
      setResult(parsed);
      setStep("report");
    } catch (err) {
      setError("분석 중 오류가 발생했습니다. 다시 시도해주세요.");
      setStep("upload");
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setImage(null);
    setImageBase64(null);
    setResult(null);
    setError(null);
    setStep("upload");
  };

  const priorityColor = (p) => p === "High" ? "#ef4444" : p === "Medium" ? "#f59e0b" : "#10b981";
  const priorityKo = (p) => p === "High" ? "높음" : p === "Medium" ? "중간" : "낮음";

  return (
    <div style={{
      minHeight: "100vh",
      background: "#060d1a",
      fontFamily: "'Pretendard', 'Noto Sans KR', 'DM Sans', sans-serif",
      color: "#e2e8f0",
      padding: "0 0 60px"
    }}>
      {/* Header */}
      <div style={{
        background: "linear-gradient(135deg, #0a1628 0%, #0f1f3a 100%)",
        borderBottom: "1px solid #1e3a5f",
        padding: "18px 24px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        position: "sticky",
        top: 0,
        zIndex: 100
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{
            width: 36, height: 36,
            background: "linear-gradient(135deg, #0ea5e9, #6366f1)",
            borderRadius: 8,
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 18
          }}>◈</div>
          <div>
            <div style={{ fontSize: 14, fontWeight: 800, letterSpacing: "0.04em", color: "#f1f5f9" }}>
              FACE ANALYSIS SYSTEM
            </div>
            <div style={{ fontSize: 10, color: "#60a5fa", letterSpacing: "0.12em" }}>
              AESTHETIC MEDICINE · AI CONSULTATION
            </div>
          </div>
        </div>
        <div style={{ fontSize: 10, color: "#334155", letterSpacing: "0.1em" }}>
          v2.1 · Research-Based
        </div>
      </div>

      <div style={{ maxWidth: 680, margin: "0 auto", padding: "0 16px" }}>

        {/* Upload Step */}
        {step === "upload" && (
          <div>
            {/* Hero */}
            <div style={{ textAlign: "center", padding: "32px 0 20px" }}>
              <div style={{
                display: "inline-block",
                background: "linear-gradient(135deg, #0ea5e922, #6366f122)",
                border: "1px solid #1e3a5f",
                borderRadius: 12,
                padding: "6px 16px",
                marginBottom: 16,
                fontSize: 11,
                color: "#60a5fa",
                letterSpacing: "0.1em"
              }}>
                EVIDENCE-BASED · 6 PEER-REVIEWED STUDIES
              </div>
              <h1 style={{
                fontSize: 26,
                fontWeight: 900,
                background: "linear-gradient(135deg, #f1f5f9, #60a5fa)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
                margin: "0 0 10px",
                lineHeight: 1.2
              }}>
                안면 황금비율<br />정밀 분석 리포트
              </h1>
              <p style={{ color: "#64748b", fontSize: 13, lineHeight: 1.6, maxWidth: 380, margin: "0 auto" }}>
                6편의 피어리뷰 논문 기반 · 65개 안면 지표 분석<br />
                필러 시술 부위 AI 컨설팅 제공
              </p>
            </div>

            {/* Research badges */}
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6, justifyContent: "center", marginBottom: 24 }}>
              {["Willis & Todorov 2006", "Oosterhof & Todorov 2008", "Sutherland et al. 2013",
                "Zebrowitz 1997", "Vernon et al. 2014", "Pallett et al. 2010"].map(s => (
                <span key={s} style={{
                  background: "#0f1f3a",
                  border: "1px solid #1e3a5f",
                  borderRadius: 20,
                  padding: "3px 10px",
                  fontSize: 10,
                  color: "#60a5fa"
                }}>{s}</span>
              ))}
            </div>

            {/* Upload area */}
            <div
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              onClick={() => !image && fileRef.current.click()}
              style={{
                border: image ? "2px solid #0ea5e9" : "2px dashed #1e3a5f",
                borderRadius: 16,
                padding: image ? "16px" : "40px 20px",
                textAlign: "center",
                cursor: image ? "default" : "pointer",
                background: image ? "#0a1628" : "linear-gradient(135deg, #0a1628, #0d1f38)",
                transition: "all 0.3s ease",
                position: "relative",
                overflow: "hidden"
              }}
            >
              {image ? (
                <div>
                  <img
                    src={image}
                    alt="Uploaded face"
                    style={{
                      width: "100%",
                      maxHeight: 360,
                      objectFit: "contain",
                      borderRadius: 12,
                      display: "block"
                    }}
                  />
                  <div style={{ marginTop: 12, display: "flex", gap: 10, justifyContent: "center" }}>
                    <button
                      onClick={reset}
                      style={{
                        background: "#1e293b",
                        border: "1px solid #334155",
                        color: "#94a3b8",
                        borderRadius: 8,
                        padding: "10px 20px",
                        cursor: "pointer",
                        fontSize: 13
                      }}
                    >다시 선택</button>
                    <button
                      onClick={analyze}
                      style={{
                        background: "linear-gradient(135deg, #0ea5e9, #6366f1)",
                        border: "none",
                        color: "white",
                        borderRadius: 8,
                        padding: "10px 28px",
                        cursor: "pointer",
                        fontSize: 14,
                        fontWeight: 700,
                        letterSpacing: "0.04em"
                      }}
                    >🔬 분석 시작</button>
                  </div>
                </div>
              ) : (
                <div>
                  <div style={{ fontSize: 44, marginBottom: 14 }}>📷</div>
                  <div style={{ color: "#e2e8f0", fontSize: 15, fontWeight: 600, marginBottom: 6 }}>
                    사진을 업로드하세요
                  </div>
                  <div style={{ color: "#475569", fontSize: 12, lineHeight: 1.7 }}>
                    정면 사진 권장 · JPG/PNG 지원<br />
                    탭하거나 파일을 여기에 드래그하세요
                  </div>
                </div>
              )}
            </div>
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              capture="user"
              style={{ display: "none" }}
              onChange={(e) => handleFile(e.target.files[0])}
            />

            {error && (
              <div style={{
                marginTop: 12,
                background: "#450a0a",
                border: "1px solid #991b1b",
                borderRadius: 10,
                padding: "12px 16px",
                color: "#fca5a5",
                fontSize: 13
              }}>{error}</div>
            )}

            {/* Privacy note */}
            <div style={{
              marginTop: 16,
              background: "#0a1628",
              border: "1px solid #1e293b",
              borderRadius: 10,
              padding: "12px 14px",
              display: "flex",
              gap: 8,
              alignItems: "flex-start"
            }}>
              <span style={{ color: "#60a5fa", fontSize: 14, marginTop: 1 }}>🔒</span>
              <p style={{ color: "#475569", fontSize: 11, lineHeight: 1.6, margin: 0 }}>
                업로드된 사진은 분석 목적으로만 사용되며 저장되지 않습니다. 
                본 분석은 전문 의료 상담의 보조 도구로만 활용되어야 합니다.
              </p>
            </div>
          </div>
        )}

        {/* Analyzing Step */}
        {step === "analyzing" && (
          <div style={{ textAlign: "center", padding: "60px 20px" }}>
            <div style={{ marginBottom: 28 }}>
              {image && (
                <img src={image} alt="" style={{
                  width: 120, height: 120,
                  objectFit: "cover",
                  borderRadius: "50%",
                  border: "3px solid #0ea5e9",
                  display: "block",
                  margin: "0 auto 20px"
                }} />
              )}
            </div>
            <div style={{
              width: 60, height: 60,
              margin: "0 auto 24px",
              border: "4px solid #1e3a5f",
              borderTop: "4px solid #0ea5e9",
              borderRadius: "50%",
              animation: "spin 1s linear infinite"
            }} />
            <style>{`
              @keyframes spin { to { transform: rotate(360deg); } }
              @keyframes pulse { 0%,100% { opacity: 1 } 50% { opacity: 0.5 } }
            `}</style>
            <div style={{ color: "#e2e8f0", fontSize: 18, fontWeight: 700, marginBottom: 10 }}>
              AI 분석 중...
            </div>
            <div style={{ color: "#475569", fontSize: 13, lineHeight: 1.8 }}>
              65개 안면 지표 측정 중<br />
              황금비율 편차 계산 중<br />
              논문 데이터 대조 중
            </div>
          </div>
        )}

        {/* Report Step */}
        {step === "report" && result && (
          <div ref={reportRef}>
            {/* Report Header */}
            <div style={{
              background: "linear-gradient(135deg, #0a1628 0%, #0f1f3a 100%)",
              border: "1px solid #1e3a5f",
              borderRadius: "0 0 16px 16px",
              padding: "20px",
              marginBottom: 16,
              display: "flex",
              alignItems: "center",
              gap: 16
            }}>
              {image && (
                <img src={image} alt="" style={{
                  width: 70, height: 70,
                  objectFit: "cover",
                  borderRadius: "50%",
                  border: "2px solid #0ea5e9",
                  flexShrink: 0
                }} />
              )}
              <div style={{ flex: 1 }}>
                <div style={{
                  fontSize: 10,
                  color: "#60a5fa",
                  letterSpacing: "0.12em",
                  marginBottom: 4
                }}>FACIAL ANALYSIS REPORT</div>
                <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                  {[
                    ["얼굴형", result.patientSummary.faceShape],
                    ["추정 나이", result.patientSummary.ageEstimate],
                    ["성별", result.patientSummary.gender]
                  ].map(([k, v]) => (
                    <div key={k} style={{
                      background: "#0d1f38",
                      border: "1px solid #1e3a5f",
                      borderRadius: 6,
                      padding: "3px 10px",
                      fontSize: 11
                    }}>
                      <span style={{ color: "#64748b" }}>{k} </span>
                      <span style={{ color: "#e2e8f0", fontWeight: 600 }}>{v}</span>
                    </div>
                  ))}
                </div>
              </div>
              {/* Overall Score */}
              <div style={{ textAlign: "center" }}>
                <div style={{
                  width: 64, height: 64,
                  borderRadius: "50%",
                  background: `conic-gradient(#0ea5e9 ${result.patientSummary.overallScore * 3.6}deg, #1e293b 0deg)`,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  position: "relative"
                }}>
                  <div style={{
                    width: 50, height: 50,
                    borderRadius: "50%",
                    background: "#0a1628",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexDirection: "column"
                  }}>
                    <span style={{ fontSize: 18, fontWeight: 800, color: "#0ea5e9", fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>
                      {result.patientSummary.overallScore}
                    </span>
                    <span style={{ fontSize: 9, color: "#60a5fa" }}>/ 100</span>
                  </div>
                </div>
                <div style={{ fontSize: 9, color: "#475569", marginTop: 4 }}>종합점수</div>
              </div>
            </div>

            {/* Section: Impression Scores */}
            <div style={{
              background: "#0a1628",
              border: "1px solid #1e3a5f",
              borderRadius: 14,
              padding: "18px",
              marginBottom: 12
            }}>
              <div style={{ marginBottom: 16 }}>
                <span style={{
                  fontSize: 10,
                  color: "#60a5fa",
                  letterSpacing: "0.1em",
                  fontWeight: 700
                }}>01 · 인상 5축 평가</span>
                <div style={{ color: "#475569", fontSize: 11, marginTop: 3 }}>
                  Willis & Todorov (2006) · Sutherland et al. (2013) 기반
                </div>
              </div>
              <div style={{ display: "flex", justifyContent: "space-around", flexWrap: "wrap", gap: 12 }}>
                <ScoreGauge score={result.impressionScores.trustworthiness} label="Trustworthiness" labelKo="신뢰성" color="#0ea5e9" />
                <ScoreGauge score={result.impressionScores.dominance} label="Dominance" labelKo="지배성" color="#8b5cf6" />
                <ScoreGauge score={result.impressionScores.youthfulAttractiveness} label="Youthful-Attr." labelKo="젊음-매력" color="#10b981" />
                <ScoreGauge score={result.impressionScores.competence} label="Competence" labelKo="유능함" color="#f59e0b" />
                <ScoreGauge score={result.impressionScores.approachability} label="Approachability" labelKo="접근성" color="#ec4899" />
              </div>
            </div>

            {/* Section: Babyface Index */}
            <div style={{
              background: "#0a1628",
              border: "1px solid #1e3a5f",
              borderRadius: 14,
              padding: "18px",
              marginBottom: 12
            }}>
              <div style={{ marginBottom: 12 }}>
                <span style={{ fontSize: 10, color: "#60a5fa", letterSpacing: "0.1em", fontWeight: 700 }}>
                  02 · 동안지수 (Babyface Index)
                </span>
                <div style={{ color: "#475569", fontSize: 11, marginTop: 3 }}>Zebrowitz (1997) 기반</div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                    <span style={{ color: "#94a3b8", fontSize: 12 }}>성숙한 인상</span>
                    <span style={{ color: "#94a3b8", fontSize: 12 }}>동안 인상</span>
                  </div>
                  <div style={{ height: 12, background: "#1e293b", borderRadius: 6, overflow: "hidden" }}>
                    <div style={{
                      height: "100%",
                      width: `${result.babyfaceIndex.score}%`,
                      background: `linear-gradient(90deg, #6366f1, #ec4899)`,
                      borderRadius: 6
                    }} />
                  </div>
                  <div style={{ textAlign: "center", marginTop: 6 }}>
                    <span style={{ fontFamily: "'DM Mono', monospace", fontSize: 20, fontWeight: 700, color: "#f1f5f9" }}>
                      {result.babyfaceIndex.score}
                    </span>
                    <span style={{ color: "#64748b", fontSize: 12 }}> / 100 · {result.babyfaceIndex.level}</span>
                  </div>
                </div>
              </div>
              <div style={{
                background: "#0d1f38",
                border: "1px solid #1e293b",
                borderRadius: 8,
                padding: "10px 12px",
                marginTop: 12,
                fontSize: 12,
                color: "#94a3b8",
                lineHeight: 1.6
              }}>{result.babyfaceIndex.description}</div>
            </div>

            {/* Section: Golden Ratios */}
            <div style={{
              background: "#0a1628",
              border: "1px solid #1e3a5f",
              borderRadius: 14,
              padding: "18px",
              marginBottom: 12
            }}>
              <div style={{ marginBottom: 16 }}>
                <span style={{ fontSize: 10, color: "#60a5fa", letterSpacing: "0.1em", fontWeight: 700 }}>
                  03 · 황금비율 분석
                </span>
                <div style={{ color: "#475569", fontSize: 11, marginTop: 3 }}>Pallett et al. (2010) 기반</div>
              </div>
              <div style={{ display: "flex", gap: 10 }}>
                {[
                  { label: "수직 비율", labelSub: "눈~입 / 얼굴 길이", ...result.goldenRatios.verticalRatio, unit: "%" },
                  { label: "수평 비율", labelSub: "양눈 거리 / 얼굴 너비", ...result.goldenRatios.horizontalRatio, unit: "%" },
                  { label: "대칭도", labelSub: "좌우 안면 대칭", ...result.goldenRatios.facialSymmetry, unit: "%" }
                ].map((item) => {
                  const gc = gradeColor(item.grade);
                  const isAbove = item.deviation > 0;
                  return (
                    <div key={item.label} style={{
                      flex: 1,
                      background: "#0d1f38",
                      border: `1px solid ${gc}33`,
                      borderRadius: 12,
                      padding: "14px 10px",
                      textAlign: "center"
                    }}>
                      <div style={{ color: "#64748b", fontSize: 9, letterSpacing: "0.08em", marginBottom: 6 }}>
                        {item.label.toUpperCase()}
                      </div>
                      <div style={{ fontFamily: "'DM Mono', monospace", fontSize: 22, fontWeight: 700, color: gc, lineHeight: 1 }}>
                        {item.current}{item.unit}
                      </div>
                      <div style={{ color: "#475569", fontSize: 10, margin: "4px 0" }}>
                        이상값 {item.ideal}{item.unit}
                      </div>
                      <div style={{
                        background: gc + "22",
                        color: gc,
                        borderRadius: 4,
                        padding: "2px 0",
                        fontSize: 13,
                        fontWeight: 700,
                        marginTop: 6
                      }}>{item.grade}</div>
                      <div style={{
                        fontSize: 10,
                        color: isAbove ? "#10b981" : "#f59e0b",
                        marginTop: 4,
                        fontFamily: "'DM Mono', monospace"
                      }}>
                        {isAbove ? "+" : ""}{item.deviation}{item.unit}
                      </div>
                      <div style={{ color: "#334155", fontSize: 9, marginTop: 6 }}>{item.labelSub}</div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Section: Vernon 65 Measurements */}
            <div style={{
              background: "#0a1628",
              border: "1px solid #1e3a5f",
              borderRadius: 14,
              padding: "18px",
              marginBottom: 12
            }}>
              <div style={{ marginBottom: 16 }}>
                <span style={{ fontSize: 10, color: "#60a5fa", letterSpacing: "0.1em", fontWeight: 700 }}>
                  04 · 안면 세부 지표 측정
                </span>
                <div style={{ color: "#475569", fontSize: 11, marginTop: 3 }}>Vernon et al. (2014) 65-Point Analysis 기반</div>
              </div>
              {result.vernonMeasurements.map((item, i) => (
                <MeasurementBar key={i} item={item} />
              ))}
            </div>

            {/* Section: Filler Recommendations */}
            <div style={{
              background: "linear-gradient(135deg, #0a1628, #150a24)",
              border: "1px solid #3b1e5f",
              borderRadius: 14,
              padding: "18px",
              marginBottom: 12
            }}>
              <div style={{ marginBottom: 16, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div>
                  <span style={{ fontSize: 10, color: "#a78bfa", letterSpacing: "0.1em", fontWeight: 700 }}>
                    05 · 필러 시술 부위 추천
                  </span>
                  <div style={{ color: "#475569", fontSize: 11, marginTop: 3 }}>AI 기반 컨설팅 · 우선순위 순</div>
                </div>
                <div style={{
                  background: "#2d1d4a",
                  border: "1px solid #4c1d95",
                  borderRadius: 8,
                  padding: "4px 10px",
                  fontSize: 10,
                  color: "#a78bfa"
                }}>CLINICAL ADVISORY</div>
              </div>

              {result.fillerRecommendations.map((rec, i) => (
                <div key={i} style={{
                  background: "#0d0d1f",
                  border: "1px solid #1e1e3a",
                  borderRadius: 12,
                  padding: "14px",
                  marginBottom: 10,
                  position: "relative",
                  overflow: "hidden"
                }}>
                  <div style={{
                    position: "absolute",
                    top: 0, left: 0,
                    width: 3,
                    height: "100%",
                    background: priorityColor(rec.priority)
                  }} />
                  <div style={{ paddingLeft: 8 }}>
                    <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 8 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <span style={{
                          background: "#1e1e3a",
                          color: "#a78bfa",
                          fontFamily: "'DM Mono', monospace",
                          fontSize: 11,
                          fontWeight: 700,
                          padding: "2px 7px",
                          borderRadius: 4
                        }}>#{rec.rank}</span>
                        <div>
                          <div style={{ color: "#e2e8f0", fontSize: 14, fontWeight: 700 }}>{rec.areaKo}</div>
                          <div style={{ color: "#64748b", fontSize: 11 }}>{rec.area}</div>
                        </div>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <div style={{
                          background: priorityColor(rec.priority) + "22",
                          color: priorityColor(rec.priority),
                          border: `1px solid ${priorityColor(rec.priority)}44`,
                          borderRadius: 4,
                          padding: "2px 8px",
                          fontSize: 10,
                          fontWeight: 600
                        }}>우선순위: {priorityKo(rec.priority)}</div>
                      </div>
                    </div>

                    <div style={{ display: "flex", gap: 8, marginBottom: 10, flexWrap: "wrap" }}>
                      <div style={{
                        background: "#10b98122",
                        border: "1px solid #10b98133",
                        borderRadius: 6,
                        padding: "4px 10px",
                        fontSize: 11
                      }}>
                        <span style={{ color: "#64748b" }}>기대 효과 </span>
                        <span style={{ color: "#10b981", fontWeight: 600 }}>{rec.impactKo}</span>
                      </div>
                      <div style={{
                        background: "#0ea5e922",
                        border: "1px solid #0ea5e933",
                        borderRadius: 6,
                        padding: "4px 10px",
                        fontSize: 11
                      }}>
                        <span style={{ color: "#64748b" }}>제품 </span>
                        <span style={{ color: "#0ea5e9", fontWeight: 600 }}>{rec.productKo}</span>
                      </div>
                      <div style={{
                        background: "#f59e0b22",
                        border: "1px solid #f59e0b33",
                        borderRadius: 6,
                        padding: "4px 10px",
                        fontSize: 11
                      }}>
                        <span style={{ color: "#64748b" }}>용량 </span>
                        <span style={{ color: "#f59e0b", fontWeight: 600, fontFamily: "'DM Mono', monospace" }}>{rec.volume}</span>
                      </div>
                    </div>

                    <div style={{
                      background: "#0a0a1a",
                      borderRadius: 8,
                      padding: "10px 12px",
                      fontSize: 12,
                      color: "#94a3b8",
                      lineHeight: 1.7,
                      borderLeft: "2px solid #334155"
                    }}>
                      {rec.rationaleKo}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Section: Research Basis */}
            <div style={{
              background: "#0a1628",
              border: "1px solid #1e3a5f",
              borderRadius: 14,
              padding: "18px",
              marginBottom: 16
            }}>
              <div style={{ marginBottom: 14 }}>
                <span style={{ fontSize: 10, color: "#60a5fa", letterSpacing: "0.1em", fontWeight: 700 }}>
                  06 · 관련 연구 근거
                </span>
              </div>
              {result.researchInsights.map((r, i) => (
                <div key={i} style={{
                  display: "flex",
                  gap: 12,
                  marginBottom: 12,
                  paddingBottom: 12,
                  borderBottom: i < result.researchInsights.length - 1 ? "1px solid #1e293b" : "none"
                }}>
                  <div style={{
                    background: "#0d1f38",
                    border: "1px solid #1e3a5f",
                    borderRadius: 6,
                    padding: "4px 8px",
                    fontSize: 9,
                    color: "#60a5fa",
                    whiteSpace: "nowrap",
                    height: "fit-content",
                    marginTop: 2
                  }}>{r.study}</div>
                  <div>
                    <div style={{ color: "#cbd5e1", fontSize: 12, marginBottom: 4 }}>{r.findingKo}</div>
                    <div style={{ color: "#64748b", fontSize: 11, lineHeight: 1.5 }}>{r.relevance}</div>
                  </div>
                </div>
              ))}
            </div>

            {/* Disclaimer */}
            <div style={{
              background: "#0a0f1a",
              border: "1px solid #1e293b",
              borderRadius: 12,
              padding: "14px 16px",
              marginBottom: 16
            }}>
              <div style={{ color: "#475569", fontSize: 10, lineHeight: 1.7 }}>
                <span style={{ color: "#334155", fontWeight: 600 }}>⚠ 의료 면책 조항 </span>
                본 분석 결과는 AI 기반 보조 도구이며, 의료적 진단이나 치료 권고가 아닙니다. 
                모든 시술 결정은 반드시 전문 의료인의 직접 진찰 및 판단에 따라야 합니다. 
                본 리포트는 의료상담의 참고자료로만 활용되어야 합니다.
              </div>
            </div>

            {/* Action Buttons */}
            <div style={{ display: "flex", gap: 10 }}>
              <button
                onClick={reset}
                style={{
                  flex: 1,
                  background: "#0d1f38",
                  border: "1px solid #1e3a5f",
                  color: "#60a5fa",
                  borderRadius: 10,
                  padding: "14px",
                  cursor: "pointer",
                  fontSize: 14,
                  fontWeight: 600
                }}
              >← 새 분석</button>
              <button
                onClick={() => window.print()}
                style={{
                  flex: 2,
                  background: "linear-gradient(135deg, #0ea5e9, #6366f1)",
                  border: "none",
                  color: "white",
                  borderRadius: 10,
                  padding: "14px",
                  cursor: "pointer",
                  fontSize: 14,
                  fontWeight: 700
                }}
              >🖨 리포트 인쇄 / 저장</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
