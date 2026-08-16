"use client";

import { useEffect, useState } from "react";
import {
  analyzeLocation,
  generateVoice,
  getLocations,
  Location,
} from "@/lib/api";
import {
  translations,
  Language,
  TranslationKey,
} from "@/lib/translations";

type AnalysisTab =
  | "trend"
  | "water"
  | "farming"
  | "planning";

export default function Home() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [district, setDistrict] = useState("");
  const [mandal, setMandal] = useState("");

  const [loadingLocations, setLoadingLocations] =
    useState(true);

  const [locationError, setLocationError] =
    useState("");

  const [usingCurrentLocation, setUsingCurrentLocation] =
    useState(false);

  const [result, setResult] = useState<any>(null);

  const [analyzing, setAnalyzing] =
    useState(false);

  const [speaking, setSpeaking] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const [analysisError, setAnalysisError] =
    useState("");

  const [activeTab, setActiveTab] =
    useState<AnalysisTab>("trend");

  const [language, setLanguage] =
    useState<Language>("en");

  const t = translations[language];

  useEffect(() => {
    const savedLanguage =
      localStorage.getItem(
        "jala-raksha-language"
      ) as Language | null;

    if (
      savedLanguage === "en" ||
      savedLanguage === "te" ||
      savedLanguage === "hi"
    ) {
      setLanguage(savedLanguage);
    }
  }, []);

  function changeLanguage(
    newLanguage: Language
  ) {
    setLanguage(newLanguage);

    localStorage.setItem(
      "jala-raksha-language",
      newLanguage
    );
  }

  useEffect(() => {
    async function loadLocations() {
      try {
        setLoadingLocations(true);

        const data = await getLocations();

        setLocations(data);
      } catch (error) {
        console.error(error);

        setLocationError(
          tUnableToLoadLocations(language)
        );
      } finally {
        setLoadingLocations(false);
      }
    }

    loadLocations();
  }, []);

  const selectedDistrict = locations.find(
    (location) =>
      location.district === district
  );

  const mandals =
    selectedDistrict?.mandals || [];

  function handleDistrictChange(
    event: React.ChangeEvent<HTMLSelectElement>
  ) {
    setDistrict(event.target.value);
    setMandal("");
    setResult(null);
    setAnalysisError("");
  }

  function handleMandalChange(
    event: React.ChangeEvent<HTMLSelectElement>
  ) {
    setMandal(event.target.value);
    setResult(null);
    setAnalysisError("");
  }

  function formatObservationDate(
    date: string
  ) {
    const locale =
      language === "te"
        ? "te-IN"
        : language === "hi"
          ? "hi-IN"
          : "en-US";

    return new Date(date).toLocaleDateString(
      locale,
      {
        month: "long",
        year: "numeric",
      }
    );
  }

  function getRiskLabel(
    classification: string
  ) {
    switch (classification) {
      case "Safe":
        return t.safe;

      case "Semi-Critical":
        return t.semiCritical;

      case "Critical":
        return t.critical;

      case "Over-Exploited":
        return t.overExploited;

      default:
        return classification;
    }
  }

  function getRiskColor(
    classification: string
  ) {
    switch (classification) {
      case "Safe":
        return "text-emerald-600";

      case "Semi-Critical":
        return "text-amber-600";

      case "Critical":
        return "text-orange-600";

      case "Over-Exploited":
        return "text-red-600";

      default:
        return "text-slate-700";
    }
  }

  function getRiskBackground(
    classification: string
  ) {
    switch (classification) {
      case "Safe":
        return "bg-emerald-50";

      case "Semi-Critical":
        return "bg-amber-50";

      case "Critical":
        return "bg-orange-50";

      case "Over-Exploited":
        return "bg-red-50";

      default:
        return "bg-slate-50";
    }
  }

  function getRiskBorder(
    classification: string
  ) {
    switch (classification) {
      case "Safe":
        return "border-emerald-200";

      case "Semi-Critical":
        return "border-amber-200";

      case "Critical":
        return "border-orange-200";

      case "Over-Exploited":
        return "border-red-200";

      default:
        return "border-slate-200";
    }
  }

  function getRiskSummary(
    classification: string
  ) {
    switch (classification) {
      case "Safe":
        return t.riskSummarySafe;

      case "Semi-Critical":
        return t.riskSummarySemiCritical;

      case "Critical":
        return t.riskSummaryCritical;

      case "Over-Exploited":
        return t.riskSummaryOverExploited;

      default:
        return t.riskSummarySemiCritical;
    }
  }

  function getAiSummary(
    classification: string,
    groundwater: number
  ) {
    if (language === "te") {
      if (classification === "Safe") {
        return `అంచనా భూగర్భ జల స్థాయి ${groundwater.toFixed(
          3
        )} మీటర్లు మరియు ప్రస్తుత పరిస్థితి సురక్షితంగా వర్గీకరించబడింది.`;
      }

      if (classification === "Semi-Critical") {
        return `అంచనా భూగర్భ జల స్థాయి ${groundwater.toFixed(
          3
        )} మీటర్లు మరియు ప్రస్తుత పరిస్థితి సెమీ-క్రిటికల్‌గా వర్గీకరించబడింది.`;
      }

      if (classification === "Critical") {
        return `అంచనా భూగర్భ జల స్థాయి ${groundwater.toFixed(
          3
        )} మీటర్లు మరియు ప్రస్తుత పరిస్థితి క్రిటికల్‌గా వర్గీకరించబడింది.`;
      }

      return `అంచనా భూగర్భ జల స్థాయి ${groundwater.toFixed(
        3
      )} మీటర్లు మరియు ప్రస్తుత పరిస్థితి అధిక వినియోగ ప్రాంతంగా వర్గీకరించబడింది.`;
    }

    if (language === "hi") {
      if (classification === "Safe") {
        return `अनुमानित भूजल स्तर ${groundwater.toFixed(
          3
        )} मीटर है और वर्तमान स्थिति सुरक्षित वर्गीकृत की गई है।`;
      }

      if (classification === "Semi-Critical") {
        return `अनुमानित भूजल स्तर ${groundwater.toFixed(
          3
        )} मीटर है और वर्तमान स्थिति अर्ध-संकटग्रस्त वर्गीकृत की गई है।`;
      }

      if (classification === "Critical") {
        return `अनुमानित भूजल स्तर ${groundwater.toFixed(
          3
        )} मीटर है और वर्तमान स्थिति संकटग्रस्त वर्गीकृत की गई है।`;
      }

      return `अनुमानित भूजल स्तर ${groundwater.toFixed(
        3
      )} मीटर है और वर्तमान स्थिति अत्यधिक दोहन वाली वर्गीकृत की गई है।`;
    }

    return `The estimated groundwater level is ${groundwater.toFixed(
      3
    )} m and the current condition is classified as ${classification}.`;
  }

  async function handleCurrentLocation() {
    if (!navigator.geolocation) {
      setLocationError(
        language === "te"
          ? "ఈ బ్రౌజర్‌లో ప్రస్తుత స్థాన సేవ అందుబాటులో లేదు."
          : language === "hi"
            ? "इस ब्राउज़र में स्थान सेवा उपलब्ध नहीं है।"
            : "Geolocation is not supported by this browser."
      );

      return;
    }

    try {
      setUsingCurrentLocation(true);
      setLocationError("");

      const position =
        await new Promise<GeolocationPosition>(
          (resolve, reject) => {
            navigator.geolocation.getCurrentPosition(
              resolve,
              reject,
              {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0,
              }
            );
          }
        );

      const {
        latitude,
        longitude,
      } = position.coords;

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL ||
        "http://127.0.0.1:8000"
        }/location/nearest?lat=${latitude}&lon=${longitude}`
      );

      if (!response.ok) {
        throw new Error(
          language === "te"
            ? "మీ సమీప ప్రాంతాన్ని కనుగొనలేకపోయాము."
            : language === "hi"
              ? "आपके निकटतम स्थान को खोजा नहीं जा सका।"
              : "Unable to find your nearest location."
        );
      }

      const data = await response.json();

      setDistrict(data.district);
      setMandal(data.mandal);
      setResult(null);
    } catch (error) {
      console.error(error);

      setLocationError(
        error instanceof Error
          ? error.message
          : language === "te"
            ? "మీ ప్రస్తుత స్థానాన్ని పొందలేకపోయాము."
            : language === "hi"
              ? "आपका वर्तमान स्थान प्राप्त नहीं किया जा सका।"
              : "Unable to get your current location."
      );
    } finally {
      setUsingCurrentLocation(false);
    }
  }

  async function handleAnalyze() {
    if (!district || !mandal) {
      return;
    }

    try {
      setAnalyzing(true);
      setAnalysisError("");
      setResult(null);
      setActiveTab("trend");

      const data = await analyzeLocation(
        district,
        mandal
      );

      setResult(data);

      setTimeout(() => {
        document
          .getElementById("analysis-result")
          ?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
      }, 150);
    } catch (error) {
      setAnalysisError(
        error instanceof Error
          ? error.message
          : language === "te"
            ? "ప్రాంతాన్ని విశ్లేషించలేకపోయాము."
            : language === "hi"
              ? "स्थान का विश्लेषण नहीं किया जा सका।"
              : "Unable to analyze location."
      );
    } finally {
      setAnalyzing(false);
    }
  }

  async function handleSpeak() {
    if (!result) {
      return;
    }

    try {
      setSpeaking(true);

      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
        setAudioUrl(null);
      }

      const classification = result.prediction.classification;
      const groundwater = Number(result.groundwater.value);

      // Uses the same multilingual summary shown on screen
      const text = getAiSummary(
        classification,
        groundwater
      );

      console.log("Voice language:", language);
      console.log("Voice text:", text);

      const audioBlob = await generateVoice(text);

      const url = URL.createObjectURL(audioBlob);
      setAudioUrl(url);

      const audio = new Audio(url);

      audio.onended = () => {
        setSpeaking(false);
        URL.revokeObjectURL(url);
      };

      audio.onerror = () => {
        setSpeaking(false);
        URL.revokeObjectURL(url);
        console.error("Unable to play generated audio.");
      };

      await audio.play();
    } catch (error) {
      console.error("Voice generation error:", error);
      setSpeaking(false);
    }
  }

  function renderTrendTab() {
    const groundwater = Number(
      result.groundwater.value
    );

    const probabilities =
      result.prediction.probabilities || {};

    const classification =
      result.prediction.classification;

    return (
      <div className="space-y-5">

        <div className="rounded-3xl border border-blue-100 bg-white p-6 shadow-sm sm:p-8">

          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">

            <div>
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-blue-600">
                {t.groundwaterTrend}
              </p>

              <h3 className="mt-2 text-xl font-bold text-slate-900">
                {t.historicalToEstimated}
              </h3>

              <p className="mt-1 text-sm text-slate-500">
                {t.trendDescription}
              </p>
            </div>

            <div className="rounded-2xl bg-blue-50 px-4 py-3">
              <p className="text-xs text-blue-500">
                {t.estimatedGroundwater}
              </p>

              <p className="mt-1 text-xl font-bold text-blue-700">
                {groundwater.toFixed(2)} m
              </p>
            </div>

          </div>

          <div className="mt-8 rounded-2xl bg-gradient-to-b from-blue-50 to-white p-4 sm:p-6">

            <div className="relative h-52">

              <div className="absolute inset-0 flex flex-col justify-between">
                {[1, 2, 3, 4].map(
                  (line) => (
                    <div
                      key={line}
                      className="border-t border-blue-100"
                    />
                  )
                )}
              </div>

              <div className="absolute inset-x-2 bottom-0 flex h-full items-end gap-1 sm:gap-2">

                {[
                  42,
                  52,
                  48,
                  62,
                  55,
                  69,
                  57,
                  74,
                  67,
                  82,
                  71,
                  78,
                ].map(
                  (height, index) => (
                    <div
                      key={index}
                      className="flex h-full flex-1 items-end"
                    >
                      <div
                        className={`w-full rounded-t-lg transition ${index === 11
                          ? "bg-blue-600"
                          : "bg-blue-200"
                          }`}
                        style={{
                          height: `${height}%`,
                        }}
                      />
                    </div>
                  )
                )}

              </div>

            </div>

            <div className="mt-4 flex justify-between text-[11px] text-slate-400">
              <span>
                {t.historicalDataLabel}
              </span>

              <span>
                {t.currentEstimate}
              </span>
            </div>

          </div>

        </div>

        <div className="rounded-3xl border border-blue-100 bg-white p-6 shadow-sm sm:p-8">

          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-blue-600">
              {t.currentWaterRisk}
            </p>

            <h3 className="mt-2 text-xl font-bold text-slate-900">
              {t.modelConfidence}
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              {t.probabilityDescription}
            </p>
          </div>

          <div className="mt-6 grid gap-3 md:grid-cols-2">

            <ProbabilityCard
              label={t.safe}
              value={Number(
                probabilities.Safe || 0
              )}
              active={
                classification === "Safe"
              }
              color="bg-emerald-500"
            />

            <ProbabilityCard
              label={t.semiCritical}
              value={Number(
                probabilities[
                "Semi-Critical"
                ] || 0
              )}
              active={
                classification ===
                "Semi-Critical"
              }
              color="bg-amber-500"
            />

            <ProbabilityCard
              label={t.critical}
              value={Number(
                probabilities.Critical || 0
              )}
              active={
                classification ===
                "Critical"
              }
              color="bg-orange-500"
            />

            <ProbabilityCard
              label={t.overExploited}
              value={Number(
                probabilities[
                "Over-Exploited"
                ] || 0
              )}
              active={
                classification ===
                "Over-Exploited"
              }
              color="bg-red-500"
            />

          </div>

        </div>
      </div>
    );
  }

  function renderWaterTab() {
    const rainfall = Number(
      result.rainfall.monthly_rainfall_mm
    );

    const rainfallDays = Number(
      result.rainfall.rainfall_days
    );

    return (
      <div className="space-y-5">

        <div className="grid gap-5 md:grid-cols-2">

          <div className="rounded-3xl border border-blue-100 bg-white p-6 shadow-sm sm:p-8">

            <div className="flex items-start justify-between">

              <div>
                <p className="text-xs font-bold uppercase tracking-[0.15em] text-blue-500">
                  {t.rainfall}
                </p>

                <p className="mt-3 text-4xl font-bold text-slate-900">
                  {rainfall.toFixed(1)}

                  <span className="ml-1 text-lg font-medium text-slate-400">
                    mm
                  </span>
                </p>

                <p className="mt-1 text-xs text-slate-400">
                  {result.rainfall.confidence ||
                    t.historicalEstimate}
                </p>
              </div>

              <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-xl">
                🌧️
              </span>

            </div>

            <div className="mt-8 flex h-32 items-end gap-2">

              {[
                35,
                52,
                42,
                68,
                55,
                76,
                Math.min(
                  rainfall / 5,
                  100
                ),
              ].map(
                (height, index) => (
                  <div
                    key={index}
                    className="flex flex-1 items-end"
                  >
                    <div
                      className={`w-full rounded-t-xl ${index === 6
                        ? "bg-blue-600"
                        : "bg-blue-200"
                        }`}
                      style={{
                        height: `${height}%`,
                      }}
                    />
                  </div>
                )
              )}

            </div>

            <div className="mt-3 flex justify-between text-[11px] text-slate-400">
              <span>
                {t.seasonalPattern}
              </span>

              <span>
                {t.currentMonth}
              </span>
            </div>

          </div>

          <div className="rounded-3xl border border-blue-100 bg-white p-6 shadow-sm sm:p-8">

            <div className="flex items-start justify-between">

              <div>
                <p className="text-xs font-bold uppercase tracking-[0.15em] text-blue-500">
                  {t.rainfallActivity}
                </p>

                <p className="mt-3 text-5xl font-bold text-slate-900">
                  {rainfallDays}
                </p>

                <p className="mt-1 text-sm text-slate-400">
                  {t.rainyDays}
                </p>
              </div>

              <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-50 text-xl">
                ☔
              </span>

            </div>

            <div className="mt-8 grid grid-cols-7 gap-2">

              {Array.from(
                { length: 31 },
                (_, index) => (
                  <div
                    key={index}
                    className={`h-5 rounded-md ${index < rainfallDays
                      ? "bg-blue-500"
                      : "bg-slate-100"
                      }`}
                  />
                )
              )}

            </div>

            <p className="mt-4 text-xs text-slate-400">
              {formatObservationDate(
                result.observation.date
              )}
            </p>

          </div>

        </div>

        <div className="rounded-3xl border border-blue-100 bg-gradient-to-r from-blue-600 to-cyan-600 p-6 text-white shadow-lg shadow-blue-200 sm:p-8">

          <p className="text-xs font-bold uppercase tracking-[0.18em] text-blue-100">
            {t.waterSavingActions}
          </p>

          <h3 className="mt-2 text-2xl font-bold">
            {t.protectWater}
          </h3>

          <div className="mt-6 grid gap-3 sm:grid-cols-2">

            {[
              t.monitorGroundwater,
              t.improveIrrigation,
              t.promoteRainwater,
              t.groundwaterRecharge,
            ].map((item) => (
              <div
                key={item}
                className="rounded-2xl bg-white/10 px-4 py-3 text-sm backdrop-blur"
              >
                ✓ {item}
              </div>
            ))}

          </div>

        </div>

      </div>
    );
  }

  function renderFarmingTab() {
    const classification =
      result.prediction.classification;

    let headline: string =
      t.planIrrigation;

    let description: string =
      t.farmingDescription;

    if (classification === "Safe") {
      headline =
        t.waterConditionsFavorable;

      description =
        t.normalFarming;
    }

    if (
      classification === "Critical"
    ) {
      headline =
        t.reduceGroundwater;

      description =
        t.farmingDescription;
    }

    if (
      classification === "Over-Exploited"
    ) {
      headline =
        t.groundwaterIntensiveRisky;

      description =
        t.farmingDescription;
    }

    return (
      <div className="space-y-5">

        <div className="overflow-hidden rounded-3xl bg-gradient-to-br from-emerald-600 to-teal-600 p-6 text-white shadow-lg shadow-emerald-100 sm:p-8">

          <div className="flex items-start gap-4">

            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-white/15 text-2xl">
              🌾
            </div>

            <div>

              <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald-100">
                {t.farmerGuidance}
              </p>

              <h3 className="mt-2 text-2xl font-bold">
                {headline}
              </h3>

              <p className="mt-3 max-w-2xl text-sm leading-6 text-emerald-50">
                {description}
              </p>

            </div>

          </div>

        </div>

        <div className="grid gap-4 md:grid-cols-2">

          <GuidanceCard
            icon="💧"
            title={t.irrigation}
            text={t.dripSprinkler}
          />

          <GuidanceCard
            icon="🌱"
            title={t.cropPlanning}
            text={t.lowerWaterDemand}
          />

          <GuidanceCard
            icon="🌧️"
            title={t.rainwater}
            text={t.captureRainfall}
          />

          <GuidanceCard
            icon="📊"
            title={t.monitor}
            text={t.trackConditions}
          />

        </div>

        <div className="rounded-3xl border border-blue-100 bg-blue-50 p-6">

          <p className="font-semibold text-slate-900">
            {t.important}
          </p>

          <p className="mt-2 text-sm leading-6 text-slate-600">
            {t.cropDisclaimer}
          </p>

        </div>

      </div>
    );
  }

  function renderPlanningTab() {
    const classification =
      result.prediction.classification;

    let headline: string =
      t.verifyWater;

    let description: string =
      t.highDemandAssessment;

    if (
      classification === "Semi-Critical"
    ) {
      headline =
        t.carefulDevelopment;

      description =
        t.highDemandAssessment;
    }

    if (
      classification === "Critical"
    ) {
      headline =
        t.strongerAssessment;

      description =
        t.significantStress;
    }

    if (
      classification === "Over-Exploited"
    ) {
      headline =
        t.avoidDependence;

      description =
        t.alternativeSources;
    }

    return (
      <div className="space-y-5">

        <div className="rounded-3xl border border-blue-100 bg-gradient-to-br from-blue-700 to-indigo-700 p-6 text-white shadow-lg shadow-blue-100 sm:p-8">

          <div className="flex items-start gap-4">

            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-white/15 text-2xl">
              🏗️
            </div>

            <div>

              <p className="text-xs font-bold uppercase tracking-[0.18em] text-blue-100">
                {t.developmentGuidance}
              </p>

              <h3 className="mt-2 text-2xl font-bold">
                {headline}
              </h3>

              <p className="mt-3 max-w-2xl text-sm leading-6 text-blue-50">
                {description}
              </p>

            </div>

          </div>

        </div>

        <div className="rounded-3xl border border-blue-100 bg-white p-6 shadow-sm">

          <h3 className="font-semibold text-slate-900">
            {t.beforeProject}
          </h3>

          <div className="mt-5 grid gap-3 md:grid-cols-2">

            {[
              t.sustainableSupply,
              t.assessAlternative,
              t.avoidUnnecessary,
              t.planRecharge,
              t.fieldAssessment,
            ].map(
              (item, index) => (
                <div
                  key={item}
                  className="flex items-start gap-3 rounded-2xl bg-blue-50 p-4"
                >

                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white">
                    {index + 1}
                  </span>

                  <p className="text-sm leading-6 text-slate-600">
                    {item}
                  </p>

                </div>
              )
            )}

          </div>

        </div>

        <div className="grid gap-4 sm:grid-cols-3">

          <SmallInfo
            icon="💧"
            title={t.waterSource}
            text={t.verifySupply}
          />

          <SmallInfo
            icon="🌧️"
            title={t.recharge}
            text={t.planRainwater}
          />

          <SmallInfo
            icon="📋"
            title={t.assessment}
            text={t.validateField}
          />

        </div>

      </div>
    );
  }

  function renderActiveTab() {
    switch (activeTab) {
      case "trend":
        return renderTrendTab();

      case "water":
        return renderWaterTab();

      case "farming":
        return renderFarmingTab();

      case "planning":
        return renderPlanningTab();

      default:
        return renderTrendTab();
    }
  }

  return (
    <main className="min-h-screen bg-[#edf6ff] text-slate-900">

      {/* NAVBAR */}
      <nav className="border-b border-blue-900/20 bg-[#073b73] text-white">

        <div className="mx-auto flex min-h-[68px] max-w-7xl items-center justify-between gap-4 px-5 py-3 sm:px-8">

          <div className="flex items-center gap-3">

            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white text-lg shadow-lg">
              💧
            </div>

            <div>
              <p className="text-sm font-bold">
                {t.appName}
              </p>

              <p className="text-[10px] uppercase tracking-[0.18em] text-blue-200">
                {t.appSubtitle}
              </p>
            </div>

          </div>

          <div className="hidden items-center gap-7 text-sm text-blue-100 lg:flex">
            <span>{t.navGroundwater}</span>
            <span>{t.navRainfall}</span>
            <span>{t.navRisk}</span>
          </div>

          <div className="flex items-center gap-2">

            <div className="hidden rounded-full bg-white/10 px-3 py-1.5 text-xs font-semibold text-blue-100 backdrop-blur sm:block">
              {t.aiDecisionSupport}
            </div>

            {/* LANGUAGE */}
            <div className="flex items-center rounded-full border border-white/20 bg-white/10 p-1 backdrop-blur">

              <LanguageButton
                active={language === "en"}
                onClick={() =>
                  changeLanguage("en")
                }
                label="EN"
              />

              <LanguageButton
                active={language === "te"}
                onClick={() =>
                  changeLanguage("te")
                }
                label="తెలుగు"
              />

              <LanguageButton
                active={language === "hi"}
                onClick={() =>
                  changeLanguage("hi")
                }
                label="हिंदी"
              />

            </div>

          </div>

        </div>

      </nav>

      {/* HERO */}
      <section className="relative overflow-hidden bg-gradient-to-br from-[#073b73] via-[#075aa6] to-[#0795c7] text-white">

        <div className="absolute -right-32 -top-32 h-96 w-96 rounded-full bg-cyan-300/20 blur-3xl" />

        <div className="absolute -bottom-40 left-10 h-96 w-96 rounded-full bg-blue-300/20 blur-3xl" />

        <div className="absolute inset-0 opacity-[0.06]">

          <div
            className="h-full w-full"
            style={{
              backgroundImage:
                "radial-gradient(circle, white 1px, transparent 1px)",
              backgroundSize: "28px 28px",
            }}
          />

        </div>

        <div className="relative mx-auto grid max-w-7xl gap-12 px-5 py-16 sm:px-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-center lg:py-24">

          <div>

            <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 text-xs font-semibold backdrop-blur">

              <span className="h-2 w-2 rounded-full bg-cyan-300" />

              {t.heroBadge}

            </div>

            <h1 className="mt-7 max-w-3xl text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">

              {t.heroTitle1}

              <span className="block text-cyan-200">
                {t.heroTitle2}
              </span>

            </h1>

            <p className="mt-6 max-w-2xl text-base leading-7 text-blue-100 sm:text-lg">
              {t.heroDescription}
            </p>

            <div className="mt-8 flex flex-wrap gap-3">

              <HeroFeature
                icon="📊"
                text={t.historicalData}
              />

              <HeroFeature
                icon="🌧️"
                text={t.rainfallPatterns}
              />

              <HeroFeature
                icon="🤖"
                text={t.mlRiskAnalysis}
              />

            </div>

          </div>

          <div className="rounded-[2rem] border border-white/15 bg-white/10 p-5 shadow-2xl backdrop-blur-xl sm:p-7">

            <div className="flex items-center justify-between">

              <div>

                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-blue-200">
                  {t.waterIntelligence}
                </p>

                <p className="mt-1 text-xl font-bold">
                  {t.fromDataToAction}
                </p>

              </div>

              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-white/10">
                💧
              </div>

            </div>

            <div className="mt-8 flex h-44 items-end gap-2">

              {[
                35,
                49,
                42,
                62,
                53,
                70,
                61,
                79,
                67,
                84,
              ].map(
                (height, index) => (
                  <div
                    key={index}
                    className="flex flex-1 items-end"
                  >

                    <div
                      className={`w-full rounded-t-xl ${index === 9
                        ? "bg-cyan-200"
                        : "bg-white/25"
                        }`}
                      style={{
                        height: `${height}%`,
                      }}
                    />

                  </div>
                )
              )}

            </div>

            <div className="mt-5 flex items-center justify-between border-t border-white/10 pt-5">

              <div>

                <p className="text-xs text-blue-200">
                  {t.analysisPipeline}
                </p>

                <p className="mt-1 text-sm font-semibold">
                  {t.learnEstimateAct}
                </p>

              </div>

              <div className="rounded-full bg-white/10 px-3 py-1.5 text-xs text-blue-100">
                {t.aiPowered}
              </div>

            </div>

          </div>

        </div>

      </section>

      {/* LOCATION */}
      <section className="mx-auto max-w-7xl px-5 py-10 sm:px-8">

        <div className="overflow-hidden rounded-[2rem] border border-blue-100 bg-white shadow-xl shadow-blue-100/50">

          <div className="bg-gradient-to-r from-blue-50 to-cyan-50 px-6 py-7 sm:px-8">

            <p className="text-xs font-bold uppercase tracking-[0.18em] text-blue-600">
              {t.startAnalysis}
            </p>

            <h2 className="mt-2 text-2xl font-bold text-slate-900">
              {t.chooseLocation}
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              {t.chooseLocationDescription}
            </p>

          </div>

          <div className="p-6 sm:p-8">

            {locationError && (
              <div className="mb-5 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                {locationError}
              </div>
            )}

            {analysisError && (
              <div className="mb-5 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                {analysisError}
              </div>
            )}

            <div className="grid gap-5 lg:grid-cols-[1fr_1fr_auto]">

              <SelectField
                label={t.district}
                value={district}
                disabled={loadingLocations}
                onChange={
                  handleDistrictChange
                }
                placeholder={
                  loadingLocations
                    ? t.loadingDistricts
                    : t.selectDistrict
                }
                options={locations.map(
                  (location) => ({
                    label:
                      location.district,
                    value:
                      location.district,
                  })
                )}
              />

              <SelectField
                label={t.mandal}
                value={mandal}
                disabled={
                  !district ||
                  loadingLocations
                }
                onChange={
                  handleMandalChange
                }
                placeholder={
                  district
                    ? t.selectMandal
                    : t.selectDistrictFirst
                }
                options={mandals.map(
                  (item) => ({
                    label: item,
                    value: item,
                  })
                )}
              />

              <div className="flex items-end">

                <button
                  type="button"
                  onClick={handleAnalyze}
                  disabled={
                    !district ||
                    !mandal ||
                    analyzing
                  }
                  className="h-[50px] w-full rounded-xl bg-blue-600 px-7 font-semibold text-white shadow-lg shadow-blue-600/25 transition hover:-translate-y-0.5 hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40 lg:w-auto"
                >
                  {analyzing
                    ? t.analyzing
                    : t.analyzeRisk}
                </button>

              </div>

            </div>

            <div className="mt-5 flex flex-wrap items-center gap-3">

              <button
                type="button"
                onClick={
                  handleCurrentLocation
                }
                disabled={
                  usingCurrentLocation
                }
                className="inline-flex items-center gap-2 rounded-xl border border-blue-200 bg-blue-50 px-4 py-2.5 text-sm font-semibold text-blue-700 transition hover:bg-blue-100 disabled:opacity-50"
              >

                📍

                {usingCurrentLocation
                  ? t.findingLocation
                  : t.useCurrentLocation}

              </button>

              <span className="text-xs text-slate-400">
                {t.nearestLocation}
              </span>

            </div>

          </div>

        </div>

      </section>

      {/* RESULTS */}
      {result && (
        <section
          id="analysis-result"
          className="bg-gradient-to-b from-[#dff1ff] via-[#edf7ff] to-[#edf6ff] px-5 py-12 sm:px-8 sm:py-16"
        >

          <div className="mx-auto max-w-7xl">

            <div className="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">

              <div>

                <p className="text-xs font-bold uppercase tracking-[0.18em] text-blue-600">
                  {t.analysisResult}
                </p>

                <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">

                  {result.location.district}

                  <span className="mx-2 text-blue-200">
                    /
                  </span>

                  {result.location.mandal}

                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  {formatObservationDate(
                    result.observation.date
                  )}
                </p>

              </div>

              <div className="rounded-full border border-blue-200 bg-white px-4 py-2 text-xs font-semibold text-blue-600 shadow-sm">
                {t.aiDecisionSupportEstimate}
              </div>

            </div>

            {/* RISK */}
            <div
              className={`mb-5 overflow-hidden rounded-[2rem] border ${getRiskBorder(
                result.prediction
                  .classification
              )} ${getRiskBackground(
                result.prediction
                  .classification
              )} shadow-sm`}
            >

              <div className="flex flex-col justify-between gap-6 p-6 sm:flex-row sm:items-center sm:p-8">

                <div>

                  <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">
                    {t.currentWaterRisk}
                  </p>

                  <div className="mt-2 flex flex-wrap items-center gap-3">

                    <h3
                      className={`text-3xl font-bold ${getRiskColor(
                        result.prediction
                          .classification
                      )}`}
                    >
                      {getRiskLabel(
                        result.prediction
                          .classification
                      )}
                    </h3>

                    <span className="rounded-full bg-white px-3 py-1 text-xs font-bold text-slate-600 shadow-sm">
                      {(
                        result.prediction
                          .confidence * 100
                      ).toFixed(1)}
                      % {t.confidence}
                    </span>

                  </div>

                  <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
                    {getRiskSummary(
                      result.prediction
                        .classification
                    )}
                  </p>

                </div>

                <div className="hidden h-20 w-20 items-center justify-center rounded-3xl bg-white text-4xl shadow-md sm:flex">

                  {
                    result.prediction
                      .classification ===
                      "Safe"
                      ? "💧"
                      : result.prediction
                        .classification ===
                        "Semi-Critical"
                        ? "⚠️"
                        : "🚨"
                  }

                </div>

              </div>

            </div>

            {/* METRICS */}
            <div className="grid gap-5 md:grid-cols-3">

              <MetricCard
                icon="💧"
                label={t.estimatedGroundwater}
                value={`${Number(
                  result.groundwater.value
                ).toFixed(2)} m`}
                subtitle={`${formatObservationDate(
                  result.observation.date
                )} · ${t.aiEstimated}`}
              />

              <MetricCard
                icon="🌧️"
                label={t.rainfall}
                value={`${Number(
                  result.rainfall
                    .monthly_rainfall_mm
                ).toFixed(1)} mm`}
                subtitle={`${formatObservationDate(
                  result.observation.date
                )} · ${result.rainfall
                  .confidence ||
                t.historicalEstimate
                  }`}
              />

              <MetricCard
                icon="☔"
                label={t.rainfallDays}
                value={`${result.rainfall.rainfall_days}`}
                subtitle={t.estimatedRainyDays}
              />

            </div>

            {/* AI ANALYSIS */}
            <div className="mt-6 rounded-[2rem] border border-blue-100 bg-gradient-to-br from-white via-white to-blue-50/70 p-5 shadow-xl shadow-blue-100/40 sm:p-8">

              <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-start">

                <div>

                  <div className="flex items-center gap-2">

                    <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-600 text-sm text-white shadow-md shadow-blue-200">
                      ✨
                    </span>

                    <p className="text-xs font-bold uppercase tracking-[0.18em] text-blue-600">
                      {t.aiAnalysis}
                    </p>

                  </div>

                  <h2 className="mt-3 text-2xl font-bold text-slate-900">
                    {t.whatShouldYouKnow}
                  </h2>

                  <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                    {t.exploreDescription}
                  </p>

                </div>

                <span className="rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-600">
                  {formatObservationDate(
                    result.observation.date
                  )}
                </span>

              </div>

              {/* QUICK AI SUMMARY */}
              <div className="mt-6 rounded-2xl border border-blue-100 bg-blue-50/70 p-5">

                <div className="flex items-start justify-between gap-4">
                  <p className="text-sm font-semibold leading-7 text-slate-700">
                    {getAiSummary(
                      result.prediction.classification,
                      Number(result.groundwater.value)
                    )}
                  </p>

                  <button
                    type="button"
                    onClick={handleSpeak}
                    disabled={speaking}
                    className="shrink-0 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {speaking ? "🔊 Speaking..." : "🔊 Listen"}
                  </button>
                </div>

              </div>

              {/* TABS */}
              <div className="mt-7 rounded-2xl border border-blue-100 bg-blue-50/70 p-1">

                <div className="grid grid-cols-4 gap-1">

                  <AnalysisTabButton
                    active={
                      activeTab ===
                      "trend"
                    }
                    onClick={() =>
                      setActiveTab(
                        "trend"
                      )
                    }
                    label={`📈 ${t.trend}`}
                  />

                  <AnalysisTabButton
                    active={
                      activeTab ===
                      "water"
                    }
                    onClick={() =>
                      setActiveTab(
                        "water"
                      )
                    }
                    label={`💧 ${t.water}`}
                  />

                  <AnalysisTabButton
                    active={
                      activeTab ===
                      "farming"
                    }
                    onClick={() =>
                      setActiveTab(
                        "farming"
                      )
                    }
                    label={`🌾 ${t.farming}`}
                  />

                  <AnalysisTabButton
                    active={
                      activeTab ===
                      "planning"
                    }
                    onClick={() =>
                      setActiveTab(
                        "planning"
                      )
                    }
                    label={`🏗️ ${t.planning}`}
                  />

                </div>

              </div>

              <div className="pt-6">
                {renderActiveTab()}
              </div>

              <div className="mt-8 rounded-2xl border border-blue-100 bg-blue-50/60 p-4">

                <p className="text-xs leading-5 text-blue-700">
                  ⚠️ {t.disclaimer}
                </p>

              </div>

            </div>

          </div>

        </section>
      )}

      {/* EMPTY */}
      {!result && !analyzing && (
        <section className="mx-auto max-w-7xl px-5 pb-20 sm:px-8">

          <div className="overflow-hidden rounded-[2rem] border border-blue-100 bg-white shadow-lg shadow-blue-100/40">

            <div className="bg-gradient-to-r from-blue-600 to-cyan-500 px-6 py-8 text-white sm:px-8">

              <p className="text-xs font-bold uppercase tracking-[0.18em] text-blue-100">
                {t.readyWhenYouAre}
              </p>

              <h2 className="mt-2 text-2xl font-bold">
                {t.exploreGroundwater}
              </h2>

              <p className="mt-2 max-w-xl text-sm leading-6 text-blue-50">
                {t.exploreDescriptionEmpty}
              </p>

            </div>

            <div className="grid gap-4 p-6 sm:grid-cols-3 sm:p-8">

              <EmptyFeature
                icon="📊"
                title={t.estimate}
                text={
                  t.learnHistorical
                }
              />

              <EmptyFeature
                icon="🌧️"
                title={t.understand}
                text={t.seeRainfall}
              />

              <EmptyFeature
                icon="🎯"
                title={t.decide}
                text={
                  t.practicalGuidance
                }
              />

            </div>

          </div>

        </section>
      )}

      {/* FOOTER */}
      <footer className="border-t border-blue-900/30 bg-[#062f5c] text-blue-100">

        <div className="mx-auto flex max-w-7xl flex-col gap-2 px-5 py-8 text-xs sm:flex-row sm:items-center sm:justify-between sm:px-8">

          <p className="font-medium">
            {t.footer}
          </p>

          <p className="text-blue-300">
            {t.footerDescription}
          </p>

        </div>

      </footer>

    </main>
  );
}

/* ------------------------------------------------ */
/* HELPERS */
/* ------------------------------------------------ */

function tUnableToLoadLocations(
  language: Language
) {
  if (language === "te") {
    return "ప్రాంతాలను లోడ్ చేయలేకపోయాము. Backend నడుస్తుందో లేదో తనిఖీ చేయండి.";
  }

  if (language === "hi") {
    return "स्थान लोड नहीं किए जा सके। सुनिश्चित करें कि backend चल रहा है।";
  }

  return "Unable to load locations. Make sure the backend is running.";
}

/* ------------------------------------------------ */
/* COMPONENTS */
/* ------------------------------------------------ */

function SelectField({
  label,
  value,
  disabled,
  onChange,
  placeholder,
  options,
}: {
  label: string;
  value: string;
  disabled: boolean;
  onChange: (
    event: React.ChangeEvent<HTMLSelectElement>
  ) => void;
  placeholder: string;
  options: {
    label: string;
    value: string;
  }[];
}) {
  return (
    <div>

      <label className="mb-2 block text-xs font-bold uppercase tracking-[0.14em] text-blue-500">
        {label}
      </label>

      <select
        value={value}
        disabled={disabled}
        onChange={onChange}
        className="h-[50px] w-full rounded-xl border border-blue-100 bg-blue-50/50 px-4 text-sm font-medium text-slate-700 outline-none transition focus:border-blue-400 focus:bg-white focus:ring-4 focus:ring-blue-100 disabled:cursor-not-allowed disabled:opacity-50"
      >

        <option value="">
          {placeholder}
        </option>

        {options.map(
          (option) => (
            <option
              key={option.value}
              value={option.value}
            >
              {option.label}
            </option>
          )
        )}

      </select>

    </div>
  );
}

function HeroFeature({
  icon,
  text,
}: {
  icon: string;
  text: string;
}) {
  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-2 text-xs font-semibold text-blue-50 backdrop-blur">
      <span>{icon}</span>
      {text}
    </div>
  );
}

function MetricCard({
  icon,
  label,
  value,
  subtitle,
}: {
  icon: string;
  label: string;
  value: string;
  subtitle: string;
}) {
  return (
    <div className="group rounded-3xl border border-blue-100 bg-white p-6 shadow-lg shadow-blue-100/30 transition hover:-translate-y-1 hover:shadow-xl">

      <div className="flex items-center justify-between">

        <p className="text-xs font-bold uppercase tracking-[0.12em] text-blue-500">
          {label}
        </p>

        <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-lg transition group-hover:bg-blue-600 group-hover:text-white">
          {icon}
        </span>

      </div>

      <p className="mt-5 text-3xl font-bold tracking-tight text-slate-900">
        {value}
      </p>

      <p className="mt-2 text-xs leading-5 text-slate-400">
        {subtitle}
      </p>

    </div>
  );
}

function ProbabilityCard({
  label,
  value,
  active,
  color,
}: {
  label: string;
  value: number;
  active: boolean;
  color: string;
}) {
  const percentage = Math.max(
    0,
    Math.min(
      value * 100,
      100
    )
  );

  return (
    <div
      className={`rounded-2xl border p-4 transition ${active
        ? "border-blue-200 bg-blue-50/70 shadow-sm"
        : "border-slate-100 bg-white"
        }`}
    >

      <div className="flex items-center justify-between">

        <span
          className={`text-sm ${active
            ? "font-bold text-slate-900"
            : "text-slate-500"
            }`}
        >
          {label}
        </span>

        <span className="text-sm font-bold text-slate-700">
          {percentage.toFixed(1)}%
        </span>

      </div>

      <div className="mt-3 h-2.5 rounded-full bg-slate-100">

        <div
          className={`h-full rounded-full ${color}`}
          style={{
            width: `${percentage}%`,
          }}
        />

      </div>

    </div>
  );
}

function GuidanceCard({
  icon,
  title,
  text,
}: {
  icon: string;
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-3xl border border-blue-100 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-lg">

      <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-50 text-xl">
        {icon}
      </span>

      <h3 className="mt-4 font-bold text-slate-900">
        {title}
      </h3>

      <p className="mt-2 text-sm leading-6 text-slate-500">
        {text}
      </p>

    </div>
  );
}

function SmallInfo({
  icon,
  title,
  text,
}: {
  icon: string;
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-2xl border border-blue-100 bg-white p-5 shadow-sm">

      <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-lg">
        {icon}
      </span>

      <p className="mt-3 text-sm font-bold text-slate-900">
        {title}
      </p>

      <p className="mt-1 text-xs leading-5 text-slate-400">
        {text}
      </p>

    </div>
  );
}

function AnalysisTabButton({
  active,
  onClick,
  label,
}: {
  active: boolean;
  onClick: () => void;
  label: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-xl px-3 py-3 text-xs font-bold transition sm:text-sm ${active
        ? "bg-white text-blue-700 shadow-md"
        : "text-slate-500 hover:bg-white/70 hover:text-blue-600"
        }`}
    >
      {label}
    </button>
  );
}

function EmptyFeature({
  icon,
  title,
  text,
}: {
  icon: string;
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-2xl border border-blue-100 bg-blue-50/50 p-5 transition hover:bg-blue-50">

      <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-white shadow-sm">
        {icon}
      </span>

      <p className="mt-3 text-sm font-bold text-slate-800">
        {title}
      </p>

      <p className="mt-1 text-xs leading-5 text-slate-400">
        {text}
      </p>

    </div>
  );
}

function LanguageButton({
  active,
  onClick,
  label,
}: {
  active: boolean;
  onClick: () => void;
  label: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-full px-2.5 py-1.5 text-[10px] font-bold transition sm:px-3 sm:text-xs ${active
        ? "bg-white text-blue-700 shadow-sm"
        : "text-blue-100 hover:bg-white/10"
        }`}
    >
      {label}
    </button>
  );
}