-- DealFinder Database Schema
-- Based on Bauplan IDEE 5
-- Generated: 2025-01-16

-- ============ USERS & GDPR ============

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  email_verified BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_at TIMESTAMP NULL,
  gdpr_consent_given BOOLEAN DEFAULT false,
  gdpr_consent_date TIMESTAMP NULL
);

-- ============ FILTER MANAGEMENT ============

CREATE TABLE deal_filters (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(100) NOT NULL,
  categories JSONB DEFAULT '[]'::jsonb,
  price_range JSONB DEFAULT '{"min": 0, "max": 10000, "currency": "EUR"}'::jsonb,
  discount_range JSONB DEFAULT '{"min": 0, "max": 100}'::jsonb,
  min_rating DECIMAL(3,1) DEFAULT 4.0,
  min_review_count INTEGER DEFAULT 10,
  max_sales_rank INTEGER DEFAULT 100000,
  email_enabled BOOLEAN DEFAULT true,
  email_schedule JSONB DEFAULT '{"time": "06:00", "timezone": "Europe/Berlin", "days": ["MON","TUE","WED","THU","FRI"]}'::jsonb,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  is_active BOOLEAN DEFAULT true,
  CONSTRAINT unique_user_filter_name UNIQUE (user_id, name)
);

-- ============ DEALS STORAGE ============

CREATE TABLE deals (
  asin VARCHAR(10) PRIMARY KEY,
  title VARCHAR(500) NOT NULL,
  category VARCHAR(100),
  current_price DECIMAL(10,2) NOT NULL,
  original_price DECIMAL(10,2),
  discount_percent INTEGER,
  rating DECIMAL(3,1),
  review_count INTEGER,
  sales_rank INTEGER,
  amazon_url VARCHAR(500),
  image_url VARCHAR(500),
  seller_name VARCHAR(100),
  is_amazon_seller BOOLEAN,
  last_updated TIMESTAMP DEFAULT NOW()
);

-- ============ DEAL SNAPSHOTS ============

CREATE TABLE deal_snapshots (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  asin VARCHAR(10) NOT NULL REFERENCES deals(asin),
  deal_score DECIMAL(5,2),
  score_breakdown JSONB,
  spam_flag BOOLEAN DEFAULT false,
  spam_reason VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  valid_until TIMESTAMP
);

-- ============ REPORTS ============

CREATE TABLE deal_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  filter_id UUID NOT NULL REFERENCES deal_filters(id) ON DELETE CASCADE,
  deals JSONB DEFAULT '[]'::jsonb,
  deal_count INTEGER DEFAULT 0,
  generated_at TIMESTAMP DEFAULT NOW(),
  email_sent_at TIMESTAMP NULL,
  email_status VARCHAR(20) DEFAULT 'PENDING',
  email_message_id VARCHAR(255),
  open_count INTEGER DEFAULT 0,
  click_count INTEGER DEFAULT 0
);

-- ============ ANALYTICS ============

CREATE TABLE deal_clicks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  report_id UUID NOT NULL REFERENCES deal_reports(id),
  asin VARCHAR(10) NOT NULL,
  clicked_at TIMESTAMP DEFAULT NOW(),
  utm_source VARCHAR(50),
  utm_medium VARCHAR(50)
);

CREATE TABLE report_opens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  report_id UUID NOT NULL REFERENCES deal_reports(id),
  opened_at TIMESTAMP DEFAULT NOW(),
  user_agent VARCHAR(255),
  ip_address INET
);

-- ============ KEEPA API LOGGING ============

CREATE TABLE keepa_api_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  api_key_hash VARCHAR(64),
  endpoint VARCHAR(50),
  status_code INTEGER,
  request_params JSONB,
  response_summary JSONB,
  error_message VARCHAR(500),
  created_at TIMESTAMP DEFAULT NOW()
);

-- ============ GDPR COMPLIANCE ============

CREATE TABLE gdpr_consent_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  consent_type VARCHAR(20),
  given BOOLEAN,
  ip_address INET,
  user_agent VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE gdpr_deletion_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  requested_at TIMESTAMP DEFAULT NOW(),
  processed_at TIMESTAMP NULL,
  delete_personal_data BOOLEAN DEFAULT true,
  delete_reports BOOLEAN DEFAULT true,
  delete_analytics BOOLEAN DEFAULT false,
  status VARCHAR(20) DEFAULT 'PENDING'
);

-- ============ INDEXES ============

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_deleted ON users(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_filters_user_active ON deal_filters(user_id, is_active);
CREATE INDEX idx_filters_email_enabled ON deal_filters(email_enabled) WHERE is_active = true;
CREATE INDEX idx_deals_rating ON deals(rating DESC);
CREATE INDEX idx_deals_sales_rank ON deals(sales_rank ASC);
CREATE INDEX idx_deals_discount ON deals(discount_percent DESC);
CREATE INDEX idx_deals_category ON deals(category);
CREATE INDEX idx_deals_updated ON deals(last_updated DESC);
CREATE INDEX idx_snapshots_asin_time ON deal_snapshots(asin, created_at DESC);
CREATE INDEX idx_snapshots_score ON deal_snapshots(deal_score DESC);
CREATE INDEX idx_snapshots_spam ON deal_snapshots(spam_flag) WHERE spam_flag = false;
CREATE INDEX idx_snapshots_valid ON deal_snapshots(valid_until) WHERE valid_until > NOW();
CREATE INDEX idx_reports_filter_time ON deal_reports(filter_id, generated_at DESC);
CREATE INDEX idx_reports_email_status ON deal_reports(email_status);
CREATE INDEX idx_clicks_user_asin ON deal_clicks(user_id, asin);
CREATE INDEX idx_clicks_report ON deal_clicks(report_id);
CREATE INDEX idx_clicks_time ON deal_clicks(clicked_at DESC);
CREATE INDEX idx_opens_report ON report_opens(report_id);
CREATE INDEX idx_opens_time ON report_opens(opened_at DESC);
CREATE INDEX idx_keepa_status ON keepa_api_logs(status_code);
CREATE INDEX idx_keepa_time ON keepa_api_logs(created_at DESC);
CREATE INDEX idx_consent_user ON gdpr_consent_log(user_id, consent_type);
CREATE INDEX idx_deletion_status ON gdpr_deletion_requests(status);
