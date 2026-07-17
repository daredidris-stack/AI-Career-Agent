import { useEffect, useState } from "react";
import {
  Briefcase,
  Code2,
  Globe2,
  GraduationCap,
  Link,
  LoaderCircle,
  Phone,
  Save,
  Sparkles,
  UserRound,
} from "lucide-react";

import {
  createProfile,
  getProfile,
  updateProfile,
} from "../services/api";

const initialProfile = {
  phone: "",
  country: "",
  state: "",
  city: "",
  current_role: "",
  target_role: "",
  years_experience: 0,
  professional_summary: "",
  technical_skills: "",
  soft_skills: "",
  linkedin: "",
  github: "",
  portfolio: "",
  preferred_job_type: "",
  preferred_work_mode: "",
};

function Profile() {
  const [formData, setFormData] = useState(initialProfile);
  const [profileExists, setProfileExists] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadProfile() {
      try {
        const response = await getProfile();

        setFormData({
          ...initialProfile,
          ...response.data,
        });

        setProfileExists(true);
      } catch (requestError) {
        if (requestError.response?.status !== 404) {
          setError("We could not load your profile.");
        }
      } finally {
        setLoading(false);
      }
    }

    loadProfile();
  }, []);

  function handleChange(event) {
    const { name, value, type } = event.target;

    setFormData((currentData) => ({
      ...currentData,
      [name]: type === "number" ? Number(value) : value,
    }));

    setMessage("");
    setError("");
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setSaving(true);
    setMessage("");
    setError("");

    try {
      const wasExistingProfile = profileExists;

      const response = wasExistingProfile
        ? await updateProfile(formData)
        : await createProfile(formData);

      setFormData({
        ...initialProfile,
        ...response.data,
      });

      setProfileExists(true);

      setMessage(
        wasExistingProfile
          ? "Profile updated successfully."
          : "Profile created successfully."
      );
    } catch (requestError) {
      const detail = requestError.response?.data?.detail;

      setError(
        typeof detail === "string"
          ? detail
          : "We could not save your profile."
      );
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="flex items-center gap-3 text-gray-300">
          <LoaderCircle className="animate-spin" size={24} />

          <span>Loading your profile...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-4xl space-y-6 pb-8">
      <section className="rounded-2xl border border-gray-800 bg-gray-900 p-5 sm:p-7">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="mb-2 flex items-center gap-2 text-sm font-medium text-blue-400">
              <Sparkles size={16} />
              Career profile
            </div>

            <h1 className="text-2xl font-bold text-white sm:text-3xl">
              Build your professional identity
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-gray-400 sm:text-base">
              Your profile powers personalized resume analysis, job matching,
              skill recommendations, and career guidance.
            </p>
          </div>

          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-blue-600/15 text-blue-400">
            <UserRound size={28} />
          </div>
        </div>
      </section>

      <form onSubmit={handleSubmit} className="space-y-6">
        <ProfileSection
          title="Contact information"
          description="Add your phone number and current location."
          icon={<Phone size={20} />}
        >
          <VerticalFields>
            <InputField
              label="Phone"
              name="phone"
              type="tel"
              value={formData.phone}
              onChange={handleChange}
              placeholder="+52 55 0000 0000"
              autoComplete="tel"
            />

            <InputField
              label="Country"
              name="country"
              value={formData.country}
              onChange={handleChange}
              placeholder="Mexico"
              autoComplete="country-name"
            />

            <InputField
              label="State"
              name="state"
              value={formData.state}
              onChange={handleChange}
              placeholder="Querétaro"
              autoComplete="address-level1"
            />

            <InputField
              label="City"
              name="city"
              value={formData.city}
              onChange={handleChange}
              placeholder="Querétaro"
              autoComplete="address-level2"
            />
          </VerticalFields>
        </ProfileSection>

        <ProfileSection
          title="Career information"
          description="Tell NextHire AI about your current position and career direction."
          icon={<Briefcase size={20} />}
        >
          <VerticalFields>
            <InputField
              label="Current role"
              name="current_role"
              value={formData.current_role}
              onChange={handleChange}
              placeholder="Datacenter Technician"
            />

            <InputField
              label="Target role"
              name="target_role"
              value={formData.target_role}
              onChange={handleChange}
              placeholder="Cloud Engineer"
            />

            <InputField
              label="Years of experience"
              name="years_experience"
              type="number"
              min="0"
              step="1"
              value={formData.years_experience}
              onChange={handleChange}
            />

            <SelectField
              label="Preferred job type"
              name="preferred_job_type"
              value={formData.preferred_job_type}
              onChange={handleChange}
              options={[
                "Full-time",
                "Part-time",
                "Contract",
                "Internship",
                "Freelance",
              ]}
            />

            <SelectField
              label="Preferred work mode"
              name="preferred_work_mode"
              value={formData.preferred_work_mode}
              onChange={handleChange}
              options={[
                "Remote",
                "Hybrid",
                "On-site",
                "Flexible",
              ]}
            />

            <TextAreaField
              label="Professional summary"
              name="professional_summary"
              value={formData.professional_summary}
              onChange={handleChange}
              placeholder="Describe your experience, strengths, achievements, and career direction."
              rows={6}
            />
          </VerticalFields>
        </ProfileSection>

        <ProfileSection
          title="Skills"
          description="Separate each skill with a comma. Interactive skill tags can be added later."
          icon={<GraduationCap size={20} />}
        >
          <VerticalFields>
            <TextAreaField
              label="Technical skills"
              name="technical_skills"
              value={formData.technical_skills}
              onChange={handleChange}
              placeholder="AWS, Linux, Python, Networking, Docker"
              rows={5}
            />

            <TextAreaField
              label="Soft skills"
              name="soft_skills"
              value={formData.soft_skills}
              onChange={handleChange}
              placeholder="Communication, troubleshooting, leadership, teamwork"
              rows={5}
            />
          </VerticalFields>
        </ProfileSection>

        <ProfileSection
          title="Professional links"
          description="Add links that help recruiters and employers learn more about your work."
          icon={<Globe2 size={20} />}
        >
          <VerticalFields>
            <InputField
              label="LinkedIn"
              name="linkedin"
              type="url"
              value={formData.linkedin}
              onChange={handleChange}
              placeholder="https://linkedin.com/in/your-name"
              icon={<Globe2 size={18} />}
            />

            <InputField
              label="GitHub"
              name="github"
              type="url"
              value={formData.github}
              onChange={handleChange}
              placeholder="https://github.com/your-username"
              icon={<Code2 size={18} />}
            />

            <InputField
              label="Portfolio"
              name="portfolio"
              type="url"
              value={formData.portfolio}
              onChange={handleChange}
              placeholder="https://yourportfolio.com"
              icon={<Link size={18} />}
            />
          </VerticalFields>
        </ProfileSection>

        <div className="sticky bottom-4 z-20 rounded-2xl border border-gray-800 bg-gray-950/90 p-4 shadow-2xl backdrop-blur">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div aria-live="polite" className="min-h-6 text-sm">
              {message && (
                <p className="text-green-400">
                  {message}
                </p>
              )}

              {error && (
                <p className="text-red-400">
                  {error}
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={saving}
              className="
                inline-flex
                min-h-11
                w-full
                items-center
                justify-center
                gap-2
                rounded-xl
                bg-blue-600
                px-6
                py-3
                font-semibold
                text-white
                transition
                hover:bg-blue-500
                focus:outline-none
                focus:ring-2
                focus:ring-blue-400
                focus:ring-offset-2
                focus:ring-offset-gray-950
                disabled:cursor-not-allowed
                disabled:opacity-60
                sm:w-auto
              "
            >
              {saving ? (
                <LoaderCircle className="animate-spin" size={19} />
              ) : (
                <Save size={19} />
              )}

              {saving
                ? "Saving..."
                : profileExists
                  ? "Save changes"
                  : "Create profile"}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}

function ProfileSection({
  title,
  description,
  icon,
  children,
}) {
  return (
    <section className="rounded-2xl border border-gray-800 bg-gray-900 p-5 sm:p-7">
      <div className="mb-6 flex items-start gap-3">
        <div className="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gray-800 text-blue-400">
          {icon}
        </div>

        <div>
          <h2 className="text-lg font-semibold text-white">
            {title}
          </h2>

          <p className="mt-1 text-sm leading-6 text-gray-400">
            {description}
          </p>
        </div>
      </div>

      {children}
    </section>
  );
}

function VerticalFields({ children }) {
  return (
    <div className="flex flex-col gap-5">
      {children}
    </div>
  );
}

function InputField({
  label,
  icon,
  ...inputProps
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-medium text-gray-300">
        {label}
      </span>

      <div className="flex min-h-12 items-center gap-3 rounded-xl border border-gray-700 bg-gray-950 px-4 transition focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/20">
        {icon && (
          <span className="shrink-0 text-gray-500">
            {icon}
          </span>
        )}

        <input
          {...inputProps}
          className="
            min-w-0
            flex-1
            bg-transparent
            py-3
            text-white
            outline-none
            placeholder:text-gray-600
          "
        />
      </div>
    </label>
  );
}

function SelectField({
  label,
  options,
  ...selectProps
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-medium text-gray-300">
        {label}
      </span>

      <select
        {...selectProps}
        className="
          min-h-12
          w-full
          rounded-xl
          border
          border-gray-700
          bg-gray-950
          px-4
          py-3
          text-white
          outline-none
          transition
          focus:border-blue-500
          focus:ring-2
          focus:ring-blue-500/20
        "
      >
        <option value="">
          Select an option
        </option>

        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

function TextAreaField({
  label,
  ...textAreaProps
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-medium text-gray-300">
        {label}
      </span>

      <textarea
        {...textAreaProps}
        className="
          w-full
          resize-y
          rounded-xl
          border
          border-gray-700
          bg-gray-950
          px-4
          py-3
          text-white
          outline-none
          transition
          placeholder:text-gray-600
          focus:border-blue-500
          focus:ring-2
          focus:ring-blue-500/20
        "
      />
    </label>
  );
}

export default Profile;
