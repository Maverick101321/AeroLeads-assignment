class CallLog < ApplicationRecord
  belongs_to :contact
  scope :recent_first, -> { order(created_at: :desc) }
end
