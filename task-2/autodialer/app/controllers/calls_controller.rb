require "twilio-ruby"

class CallsController < ApplicationController
  skip_before_action :verify_authenticity_token

  def test
    to_number = params[:to] || "+918433907272" # safe 1800 biz/testing line

    client = Twilio::REST::Client.new(
      ENV["TWILIO_ACCOUNT_SID"],
      ENV["TWILIO_AUTH_TOKEN"]
    )

    call = client.calls.create(
      from: ENV["TWILIO_FROM_NUMBER"],
      to: to_number,
      url: "#{ENV["PUBLIC_HOST"]}/calls/twiml"
    )

    render json: { status: "ok", sid: call.sid }
  end

  def twiml
    response = Twilio::TwiML::VoiceResponse.new
    response.say(
      message: "Hello. This is a test call from your autodialer. Have a nice day.",
      voice: "Polly.Aditi" # nice Indian English voice
    )
    render xml: response.to_xml
  end
end
