class DashboardController < ApplicationController
  def index
    @contacts = Contact.order(:id)
    @call_logs = CallLog.includes(:contact).recent_first.limit(20)
  end
end