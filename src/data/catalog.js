import catalog from "./projects.json";
import handoverData from "./handover.json";

export const projects = catalog.projects;

export function imgSrc(file) {
  return `/images/projects/${file}`;
}

export function inquireHref(projectName, channel = "whatsapp") {
  const text = `Hi Crystal, I'm inquiring about ${projectName}.`;
  if (channel === "email") {
    const subject = encodeURIComponent(`Inquiry: ${projectName}`);
    return `mailto:crystalflores.rpmmc@gmail.com?subject=${subject}&body=${encodeURIComponent(text)}`;
  }
  return `https://wa.me/639776821438?text=${encodeURIComponent(text)}`;
}

/** Keep only Ready for Occupancy towers; drop pre-selling text. */
export function rfoTowers(status) {
  if (!status) return [];
  return status
    .split(/;/)
    .map((s) => s.trim())
    .filter((s) => /ready for occupancy/i.test(s))
    .map((s) => {
      const m = s.match(/Tower\s+[A-Z0-9]+/i);
      return m ? m[0].replace(/^tower/i, "Tower") : null;
    })
    .filter(Boolean);
}

export function rfoLabel(status) {
  const towers = rfoTowers(status);
  if (towers.length === 0) return "Ready for occupancy";
  if (towers.length === 1) return `${towers[0]}, ready for occupancy`;
  if (towers.length === 2) return `${towers[0]} and ${towers[1]}, ready for occupancy`;
  return `${towers.slice(0, -1).join(", ")}, and ${towers.at(-1)}, ready for occupancy`;
}


export function handoverEntries() {
  const list = handoverData.releases || [];
  return list.map((entry) => {
    const project = entry.slug ? projects.find((p) => p.slug === entry.slug) : null;
    const photo = entry.photo
      ? entry.photo
      : project?.hero?.file
        ? imgSrc(project.hero.file)
        : "";
    return {
      project: entry.project || project?.name || "",
      slug: entry.slug || project?.slug || "",
      tower_or_unit: entry.tower_or_unit || "",
      location: entry.location || project?.city || project?.location || "",
      release_date: entry.release_date || "",
      photo,
      photoWidth: project?.hero?.width,
      photoHeight: project?.hero?.height,
      note: entry.note || "",
    };
  });
}

export function rfoReleases() {
  return projects.filter((p) => p.is_rfo);
}

export const heroSlides = [
  {
    src: "/images/hero/amisa-clubhouse.webp",
    width: 2200,
    height: 1238,
    alt: "",
  },
  {
    src: "/images/hero/galleria-pool-night.webp",
    width: 1652,
    height: 825,
    alt: "",
  },
  {
    src: "/images/hero/westin-lobby.webp",
    width: 1980,
    height: 1532,
    alt: "",
  },
  {
    src: "/images/hero/aurora-lounge.webp",
    width: 2200,
    height: 1467,
    alt: "",
  },
];

export function cities() {
  return [...new Set(projects.map((p) => p.city).filter(Boolean))].sort();
}

export function featured() {
  const prefer = [
    "aurora-escalades",
    "mira",
    "le-pont-residences",
    "the-trion-towers",
    "galleria-residences-cebu",
    "amisa-private-residences",
  ];
  const map = Object.fromEntries(projects.map((p) => [p.slug, p]));
  return prefer.map((s) => map[s]).filter(Boolean);
}

export function bySlug(slug) {
  return projects.find((p) => p.slug === slug);
}

export function typeLabel(type) {
  return type === "house-and-lot" ? "House and lot" : "Condominium";
}
