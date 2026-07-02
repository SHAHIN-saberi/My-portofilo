"use client";

import AdminCrudPage, { CrudField, CrudColumn } from "@/components/AdminCrudPage";
import {
  listAdminCoursesService,
  createAdminCourseService,
  deleteAdminCourseService,
} from "@/services/admin.service";

const fields: CrudField[] = [
  { key: "provider", label: "Provider", required: true, placeholder: "e.g. Coursera, Udemy" },
  { key: "completion_date", label: "Completion Date", type: "date" },
  { key: "credential_url", label: "Credential URL", placeholder: "https://..." },
  { key: "title_en", label: "Title (EN)", required: true },
  { key: "title_fa", label: "Title (FA)" },
  { key: "description_en", label: "Description (EN)", type: "textarea" },
  { key: "description_fa", label: "Description (FA)", type: "textarea" },
];

const columns: CrudColumn[] = [
  { key: "provider", label: "Provider" },
  {
    key: "title",
    label: "Title",
    render: (item: any) =>
      item.translations?.find((t: any) => t.lang === "en")?.title || `Course #${item.id}`,
  },
  { key: "completion_date", label: "Date" },
];

export default function AdminCoursesPage() {
  return (
    <AdminCrudPage
      title="Manage Courses"
      icon="📚"
      fields={fields}
      columns={columns}
      listService={listAdminCoursesService}
      createService={createAdminCourseService}
      deleteService={deleteAdminCourseService}
      getItemTitle={(item) =>
        item.translations?.find((t: any) => t.lang === "en")?.title || `Course #${item.id}`
      }
      buildPayload={(formData) => ({
        provider: formData.provider || null,
        completion_date: formData.completion_date || null,
        credential_url: formData.credential_url || null,
        display_order: 0,
        translations: [
          {
            lang: "en",
            title: formData.title_en,
            description: formData.description_en || null,
          },
          {
            lang: "fa",
            title: formData.title_fa || formData.title_en,
            description: formData.description_fa || null,
          },
        ],
      })}
    />
  );
}
