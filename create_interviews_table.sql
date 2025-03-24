CREATE TABLE IF NOT EXISTS interviews (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL,
    user_id UUID NOT NULL,
    created_by UUID NOT NULL,
    application_id UUID REFERENCES applications(id),
    interviewer TEXT,
    interview_date TIMESTAMP WITH TIME ZONE,
    interview_type TEXT,
    result TEXT,
    feedback TEXT,
    remote_created_at TIMESTAMP WITH TIME ZONE,
    remote_updated_at TIMESTAMP WITH TIME ZONE
); 