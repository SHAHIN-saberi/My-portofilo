"use client";

import AdminCrudPage, { CrudField, CrudColumn } from "@/components/AdminCrudPage";
import {
  listAdminSocialLinksService,
  createAdminSocialLinkService,
  deleteAdminSocialLinkService,
} from "@/services/admin.service";

const fields: CrudField[] = [
  { key: "platform", label: "Platform", required: true, placeholder: "e.g. github, linkedin, twitter" },
  { key: "url", label: "URL", required: true, placeholder: "https://..." },
];

const columns: CrudColumn[] = [
  { key: "platform", label: "Platform" },
  {
    key: "url",
    label: "URL",
    render: (item: any) => (
      <a href={item.url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">
        {item.url}
      </a>
    ),
  },
];

export default function AdminSocialLinksPage() {
  return (
    <AdminCrudPage
      title="Manage Social Links"
      icon="🔗"
      fields={fields}
      columns={columns}
      listService={listAdminSocialLinksService}
      createService={createAdminSocialLinkService}
      deleteService={deleteAdminSocialLinkService}
      getItemTitle={(item) => item.platform || `Link #${item.id}`}
      buildPayload={(formData) => ({
        platform: formData.platform,
        url: formData.url,
        display_order: 0,
        is_visible: true,
      })}
    />
  );
}
