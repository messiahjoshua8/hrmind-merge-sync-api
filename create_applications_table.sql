CREATE TABLE IF NOT EXISTS applications (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL,
    user_id UUID NOT NULL,
    created_by UUID NOT NULL,
    candidate_id UUID REFERENCES candidates(id),
    job_posting_id UUID REFERENCES job_postings(id),
    status TEXT NOT NULL,
    applied_at TIMESTAMP WITH TIME ZONE,
    last_updated TIMESTAMP WITH TIME ZONE
); 