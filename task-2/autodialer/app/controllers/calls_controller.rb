require "twilio-ruby"

class CallsController < ApplicationController
  skip_before_action :verify_authenticity_token

  def start_batch
    first = Contact.where(status: "pending").order(:id).first
    if first
      DialNextJob.perform_later(first.id)
      render plain: "Dialing started with #{first.phone_number}"
    else
      render plain: "No pending contacts."
    end
  end

  def twiml
    response = Twilio::TwiML::VoiceResponse.new
    response.say(
      message: "Hello, this is a test call from your autodialer. Have a nice day.",
      voice: "Polly.Aditi"
    )
    render xml: response.to_xml
  end

  # Twilio calls this URL when call finishes
  def status
    sid     = params["CallSid"]
    status  = params["CallStatus"]
    contact = Contact.find_by(id: params["contact_id"])
    return head :ok unless contact

    contact.update(status: status, last_called_at: Time.current)

    # queue next pending contact
    next_contact = Contact.where(status: "pending").order(:id).first
    DialNextJob.perform_later(next_contact.id) if next_contact

    head :ok
  end
end
