"use client";

import AdminCrudPage, { CrudField, CrudColumn } from "@/components/AdminCrudPage";
import {
  listAdminCertificatesService,
  createAdminCertificateService,
  deleteAdminCertificateService,
} from "@/services/admin.service";

const fields: CrudField[] = [
  { key: "issuer", label: "Issuer", required: true, placeholder: "e.g. AWS, Google, Microsoft" },
  { key: "issue_date", label: "Issue Date", type: "date" },
  { key: "credential_url", label: "Credential URL", placeholder: "https://..." },
  { key: "title_en", label: "Title (EN)", required: true },
  { key: "title_fa", label: "Title (FA)" },
  { key: "description_en", label: "Description (EN)", type: "textarea" },
  { key: "description_fa", label: "Description (FA)", type: "textarea" },
];

const columns: CrudColumn[] = [
  { key: "issuer", label: "Issuer" },
  {
    key: "title",
    label: "Title",
    render: (item: any) =>
      item.translations?.find((t: any) => t.lang === "en")?.title || `Certificate #${item.id}`,
  },
  { key: "issue_date", label: "Date" },
];

export default function AdminCertificatesPage() {
  return (
    <AdminCrudPage
      title="Manage Certificates"
      icon="🏅"
      fields={fields}
      columns={columns}
      listService={listAdminCertificatesService}
      createService={createAdminCertificateService}
      deleteService={deleteAdminCertificateService}
      getItemTitle={(item) =>
        item.translations?.find((t: any) => t.lang === "en")?.title || `Certificate #${item.id}`
      }
      buildPayload={(formData) => ({
        issuer: formData.issuer || null,
        issue_date: formData.issue_date || null,
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
