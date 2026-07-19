const LINKEDIN_JOB_SEARCH_URL = "https://www.linkedin.com/jobs/search/";

const employmentTypeCodes = {
  "Full Time": "F",
  "Part Time": "P",
  Contract: "C",
  Intern: "I",
};

const postedWithinSeconds = {
  1: 86400,
  7: 604800,
  30: 2592000,
};

export function buildLinkedInJobSearchUrl({
  targetRole,
  country,
  city,
  industry,
  workMode,
  employmentType,
  postedWithinDays,
}) {
  const role = targetRole.trim();
  if (!role) {
    return "";
  }

  const url = new URL(LINKEDIN_JOB_SEARCH_URL);
  const keywords = [role, industry.trim()].filter(Boolean).join(" ");
  const location = country === "Worldwide"
    ? ""
    : [city.trim(), country.trim()].filter(Boolean).join(", ");

  url.searchParams.set("keywords", keywords);
  if (location) {
    url.searchParams.set("location", location);
  }
  if (workMode === "Remote") {
    url.searchParams.set("f_WT", "2");
  }
  if (employmentTypeCodes[employmentType]) {
    url.searchParams.set("f_JT", employmentTypeCodes[employmentType]);
  }
  if (postedWithinSeconds[postedWithinDays]) {
    url.searchParams.set("f_TPR", `r${postedWithinSeconds[postedWithinDays]}`);
  }

  return url.toString();
}
