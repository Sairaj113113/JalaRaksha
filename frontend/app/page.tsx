"use client";

import { useEffect, useState } from "react";
import { analyzeLocation, getLocations, Location } from "@/lib/api";

export default function Home() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [district, setDistrict] = useState("");
  const [mandal, setMandal] = useState("");

  const [loadingLocations, setLoadingLocations] = useState(true);
  const [locationError, setLocationError] = useState("");

  const [result, setResult] = useState<any>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisError, setAnalysisError] = useState("");

  useEffect(() => {
    async function loadLocations() {
      try {
        setLoadingLocations(true);
        const data = await getLocations();
        setLocations(data);
      } catch (error) {
        console.error(error);
        setLocationError(
          "Unable to load locations. Make sure the backend is running."
        );
      } finally {
        setLoadingLocations(false);
      }
    }

    loadLocations();
  }, []);

  const selectedDistrict = locations.find(
    (location) => location.district === district
  );

  const mandals = selectedDistrict?.mandals || [];

  function handleDistrictChange(
    event: React.ChangeEvent<HTMLSelectElement>
  ) {
    setDistrict(event.target.value);
    setMandal("");
  }

  return (
    <main className="min-h-screen bg-slate-50 px-6 py-10">
      <div className="mx-auto max-w-6xl">

        <header className="mb-10">
          <p className="mb-2 text-sm font-semibold uppercase tracking-widest text-blue-600">
            Jala Raksha
          </p>

          <h1 className="text-4xl font-bold tracking-tight text-slate-900">
            Groundwater Intelligence
          </h1>

          <p className="mt-3 max-w-2xl text-slate-600">
            Assess groundwater risk using groundwater observations,
            rainfall conditions, and machine learning.
          </p>
        </header>

        <section className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h2 className="text-xl font-semibold text-slate-900">
            Select Location
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Choose a district and mandal to analyze groundwater conditions.
          </p>

          {locationError && (
            <div className="mt-4 rounded-xl bg-red-50 p-4 text-sm text-red-700">
              {locationError}
            </div>
          )}

          <div className="mt-6 grid gap-4 md:grid-cols-2">

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                District
              </label>

              <select
                value={district}
                onChange={handleDistrictChange}
                disabled={loadingLocations}
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 outline-none focus:border-blue-500 disabled:bg-slate-100"
              >
                <option value="">
                  {loadingLocations
                    ? "Loading districts..."
                    : "Select district"}
                </option>

                {locations.map((location) => (
                  <option
                    key={location.district}
                    value={location.district}
                  >
                    {location.district}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Mandal
              </label>

              <select
                value={mandal}
                onChange={(event) => setMandal(event.target.value)}
                disabled={!district || loadingLocations}
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 outline-none focus:border-blue-500 disabled:bg-slate-100"
              >
                <option value="">
                  {district
                    ? "Select mandal"
                    : "Select district first"}
                </option>

                {mandals.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </div>

          </div>

          <div className="mt-5 flex flex-col gap-3 sm:flex-row">

            <button
              type="button"
              className="rounded-xl border border-slate-300 px-5 py-3 font-medium text-slate-700 hover:bg-slate-50"
            >
              📍 Use Current Location
            </button>

            <button
              type="button"
              onClick={handleAnalyze}
              disabled={!district || !mandal || analyzing}
              className="rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {analyzing ? "Analyzing..." : "Analyze Risk"}
            </button>

          </div>
        </section>

        {result && (
          <section className="mt-6 space-y-6">

            {/* Risk */}
            <div className="rounded-2xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
              <p className="text-sm font-semibold uppercase tracking-wider text-slate-500">
                Risk Assessment
              </p>

              <h2 className="mt-3 text-4xl font-bold text-slate-900">
                {result.prediction.classification}
              </h2>

              <p className="mt-2 text-slate-600">
                Model confidence:{" "}
                <strong>
                  {(result.prediction.confidence * 100).toFixed(0)}%
                </strong>
              </p>
            </div>

            {/* Evidence */}
            <div className="grid gap-6 md:grid-cols-3">

              <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
                <p className="text-sm text-slate-500">
                  Groundwater
                </p>

                <p className="mt-2 text-3xl font-bold text-slate-900">
                  {result.groundwater.value} {result.groundwater.unit}
                </p>
              </div>

              <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
                <p className="text-sm text-slate-500">
                  Monthly Rainfall
                </p>

                <p className="mt-2 text-3xl font-bold text-slate-900">
                  {result.rainfall.monthly_rainfall_mm} mm
                </p>
              </div>

              <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
                <p className="text-sm text-slate-500">
                  Rainfall Days
                </p>

                <p className="mt-2 text-3xl font-bold text-slate-900">
                  {result.rainfall.rainfall_days}
                </p>
              </div>

            </div>

            {/* AI Explanation */}
            <div className="rounded-2xl bg-white p-8 shadow-sm ring-1 ring-slate-200">

              <p className="text-sm font-semibold uppercase tracking-wider text-blue-600">
                AI Analysis
              </p>

              <p className="mt-4 text-slate-700">
                {result.explanation.summary}
              </p>

              <h3 className="mt-6 font-semibold text-slate-900">
                Key Factors
              </h3>
<ul className="mt-3 list-disc space-y-3 pl-5 text-slate-600">
  {result.explanation.key_factors.map(
    (factor: { factor: string; explanation: string }, index: number) => (
      <li key={`${factor.factor}-${index}`}>
        <strong className="text-slate-900">
          {factor.factor}
        </strong>
        <p className="mt-1">
          {factor.explanation}
        </p>
      </li>
    )
  )}
</ul>

              <h3 className="mt-6 font-semibold text-slate-900">
                Recommended Actions
              </h3>

              <ul className="mt-3 list-disc space-y-2 pl-5 text-slate-600">
                {result.explanation.recommendations.map(
                  (recommendation: string) => (
                    <li key={recommendation}>
                      {recommendation}
                    </li>
                  )
                )}
              </ul>

            </div>

          </section>
        )}

      </div>
    </main>
  );

  async function handleAnalyze() {
    if (!district || !mandal) return;

    try {
      setAnalyzing(true);
      setAnalysisError("");
      setResult(null);

      const data = await analyzeLocation(district, mandal);

      setResult(data);
    } catch (error) {
      setAnalysisError(
        error instanceof Error
          ? error.message
          : "Unable to analyze location."
      );
    } finally {
      setAnalyzing(false);
    }
  }
}

