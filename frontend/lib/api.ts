const API_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type Location = {
    district: string;
    mandals: string[];
};

const mockLocations: Location[] = [
    {
        district: "NALGONDA",
        mandals: [
            "Narketpalle",
            "Damaracherla",
            "Thripuraram",
            "Nampalle",
        ],
    },
    {
        district: "NIZAMABAD",
        mandals: [
            "Armoor",
            "Balkonda",
            "Bodhan",
        ],
    },
    {
        district: "ADILABAD",
        mandals: [
            "Adilabad Urban",
            "Bela",
            "Bheempoor",
            "Boath",
        ],
    },
];

export async function getLocations(): Promise<Location[]> {
    try {
        const response = await fetch(`${API_URL}/locations`, {
            cache: "no-store",
        });

        if (!response.ok) {
            throw new Error("Backend unavailable");
        }

        const data = await response.json();


        return Object.entries(data.locations).map(
            ([district, mandals]) => ({
                district,
                mandals: mandals as string[],
            })
        );
    } catch {
        console.warn("Backend unavailable. Using mock locations.");

        return mockLocations;
    }
}

export async function analyzeLocation(
    district: string,
    mandal: string
) {
    const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            district,
            mandal,
        }),
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data?.error?.message || "Analysis failed"
        );
    }

    return data;
}