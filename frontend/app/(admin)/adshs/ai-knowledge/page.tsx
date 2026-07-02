"use client";

import AdminCrudPage, { CrudField, CrudColumn } from "@/components/AdminCrudPage";
import {
  listAdminAIKnowledgeService,
  createAdminAIKnowledgeService,
  deleteAdminAIKnowledgeService,
} from "@/services/admin.service";

const fields: CrudField[] = [
  { key: "title_en", label: "Title (EN)", required: true },
  { key: "title_fa", label: "Title (FA)" },
  { key: "content_en", label: "Content (EN)", required: true, type: "textarea" },
  { key: "content_fa", label: "Content (FA)", type: "textarea" },
];

const columns: CrudColumn[] = [
  {
    key: "title",
    label: "Title",
    render: (item: any) =>
      item.translations?.find((t: any) => t.lang === "en")?.title || `Entry #${item.id}`,
  },
  {
    key: "content",
    label: "Content Preview",
    render: (item: any) => {
      const content = item.translations?.find((t: any) => t.lang === "en")?.content || "";
      return content.length > 80 ? content.substring(0, 80) + "..." : content;
    },
  },
];

export default function AdminAIKnowledgePage() {
  return (
    <AdminCrudPage
      title="Manage AI Knowledge Base"
      icon="🧠"
      fields={fields}
      columns={columns}
      listService={listAdminAIKnowledgeService}
      createService={createAdminAIKnowledgeService}
      deleteService={deleteAdminAIKnowledgeService}
      getItemTitle={(item) =>
        item.translations?.find((t: any) => t.lang === "en")?.title || `Entry #${item.id}`
      }
      buildPayload={(formData) => ({
        display_order: 0,
        translations: [
          {
            lang: "en",
            title: formData.title_en,
            content: formData.content_en,
          },
          {
            lang: "fa",
            title: formData.title_fa || formData.title_en,
            content: formData.content_fa || formData.content_en,
          },
        ],
      })}
    />
  );
}
