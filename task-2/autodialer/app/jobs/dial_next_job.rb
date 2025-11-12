class DialNextJob < ApplicationJob
  queue_as :default

  def perform(contact_id)
    contact = Contact.find(contact_id)
    return if contact.status != "pending"

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
      status_callback_event: ["completed"]
    )

    CallLog.create!(
      contact:    contact,
      status:     "started",
      sid:        call.sid,
      started_at: Time.current
    )
  rescue => e
    contact.update(status: "failed")
    CallLog.create!(
      contact: contact,
      status: "error",
      error_message: e.message
    )
  end
end
