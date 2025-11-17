class DialNextJob < ApplicationJob
  queue_as :default

  def perform(contact_id)
    contact = Contact.find(contact_id)
    return unless ["pending", "retry"].include?(contact.status)

    contact.update(status: "in_progress")

    client = Twilio::REST::Client.new(
      ENV["TWILIO_ACCOUNT_SID"],
      ENV["TWILIO_AUTH_TOKEN"]
    )

    call = client.calls.create(
      from: ENV["TWILIO_FROM_NUMBER"],
      to:   contact.phone_number,
      url:  "#{ENV["PUBLIC_HOST"]}/calls/twiml",
      status_callback: "#{ENV["PUBLIC_HOST"]}/calls/status?contact_id=#{contact.id}",
      status_callback_event: ["initiated", "ringing", "answered", "completed", "busy", "failed", "no-answer", "canceled"]
    )

    CallLog.create!(
      contact:    contact,
      status:     "started",
      sid:        call.sid,
      started_at: Time.current
    )
  rescue => e
    contact.update(status: "failed", last_called_at: Time.current)
    CallLog.create!(
      contact: contact,
      status: "error",
      error_message: e.message
    )

    # 🔁 move on to the next pending number even if this one failed
    next_contact = Contact.where(status: "pending").order(:id).first
    DialNextJob.perform_later(next_contact.id) if next_contact
  end
end
