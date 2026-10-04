from dataclasses import dataclass


@dataclass(frozen=True)
class DemoDocument:
    name: str
    location: str
    content: str
    duplicate_of: str | None = None


DEMO_DOCUMENTS: list[DemoDocument] = [
    DemoDocument("resume_final.pdf", "Documents/Career", "Resume for Amina Khan. AI engineer candidate with FastAPI, React, Python, vector search, RAG systems, internship projects, and model evaluation experience."),
    DemoDocument("resume_final_copy.pdf", "Downloads", "", duplicate_of="resume_final.pdf"),
    DemoDocument("resume_old.pdf", "Downloads", "Older resume draft for Amina Khan from 2024. Includes university coursework and early Python automation work, but excludes recent AI workspace and retrieval projects."),
    DemoDocument("machine_learning_notes.txt", "Downloads", "Lecture notes on supervised learning, loss functions, gradient descent, neural networks, embeddings, retrieval systems, and evaluation metrics for machine learning experiments."),
    DemoDocument("attention_mechanism_notes.md", "Research", "# Attention notes\nSelf attention compares query, key, and value representations so a model can focus on relevant tokens. Multi-head attention improves contextual reasoning in neural language models."),
    DemoDocument("AI_research_paper.pdf", "Downloads", "Research paper summary: vector databases, retrieval augmented generation, semantic embeddings, transformer architectures, reranking, and responsible evaluation of AI agents."),
    DemoDocument("internship_application.docx", "Downloads", "Internship application packet for an AI Engineering Associate role. Includes cover letter, resume notes, project summaries, and interview preparation checklist."),
    DemoDocument("project_requirements.pdf", "Projects/NEXORA", "Product requirements for NEXORA. Build a local-first AI workspace intelligence agent with document ingestion, semantic search, duplicate detection, safety approvals, and rollback."),
    DemoDocument("meeting_notes.txt", "Documents", "Meeting notes: discuss MVP scope, scanner service, SQLite metadata store, FastAPI endpoints, React workspace shell, safety layer, and demo script for reviewers."),
    DemoDocument("invoice_september.pdf", "Downloads", "Invoice September 2026. Cloud GPU rental, vector database prototype hosting, SaaS subscriptions, and office expenses. Total due 1840 USD."),
    DemoDocument("invoice_september_copy.pdf", "Finance", "", duplicate_of="invoice_september.pdf"),
    DemoDocument("FYP_notes.txt", "Downloads", "Final year project notes for university. The project explores computer vision, image classification, neural network training, and a research report for the supervisor."),
    DemoDocument("computer_vision_research.txt", "Research", "Computer vision research notes covering convolutional networks, object detection, segmentation datasets, confusion matrices, precision, recall, and model deployment."),
    DemoDocument("budget.txt", "Downloads", "Personal budget for September and October. Rent, electricity, internet, research conference fee, books, groceries, and savings target."),
    DemoDocument("research_summary.md", "Downloads", "Summary of AI research directions: retrieval, embeddings, transformer attention, semantic similarity, local models, document understanding, and safe agentic actions."),
    DemoDocument("random_notes.txt", "Downloads", "Remember to clean desktop, submit reimbursement, organize files, buy notebooks, renew library membership, and archive old screenshots."),
    DemoDocument("notes_43.txt", "Downloads", "Dense notes about contextual token weighting, query-key-value scoring, long-range dependency handling, and why modern language architectures reason over relationships."),
    DemoDocument("capstone_timeline.md", "University", "University capstone timeline: proposal submission, literature review, dataset preparation, model training, FYP demo, viva preparation, and final report deadline."),
    DemoDocument("thesis_literature_review.docx", "Downloads", "Literature review for a final-year project about neural retrieval, semantic document clustering, embeddings, transformer encoders, and local-first AI assistants."),
    DemoDocument("cover_letter_ai_role.docx", "Documents/Career", "Cover letter for AI engineering internship. Highlights FastAPI, TypeScript, ML prototypes, safety-minded product thinking, and shipping polished demos."),
    DemoDocument("receipt_laptop_repair.pdf", "Downloads", "Receipt for laptop repair, SSD replacement, thermal paste service, and keyboard cleaning. Paid by card in September 2026."),
    DemoDocument("nexora_architecture.md", "Projects/NEXORA", "Architecture plan: scanner, extractor, hashing engine, embedding service, vector index, orchestrator, planner, safety permission layer, sandbox executor, and rollback log."),
    DemoDocument("dataset_sources.txt", "University", "Dataset sources for computer vision FYP: open images, traffic sign collections, annotation schema, validation split, and ethical data handling notes."),
    DemoDocument("screenshot_index.txt", "Screenshots", "Screenshot inventory from downloads: product mockup, settings modal, duplicate review panel, search results, and organization approval flow."),
    DemoDocument("travel_plan.md", "Documents/Personal", "Personal travel plan with train schedule, hotel address, packing list, reimbursement reminders, and emergency contacts."),
    DemoDocument("old_invoice_august.pdf", "Finance", "Invoice August 2026. Internet bill, developer tooling subscription, cloud storage, domain renewal, and local workspace backup drive."),
]
