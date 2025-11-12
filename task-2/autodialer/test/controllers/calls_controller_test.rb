require "test_helper"

class CallsControllerTest < ActionDispatch::IntegrationTest
  test "should get create" do
    get calls_create_url
    assert_response :success
  end

  test "should get status" do
    get calls_status_url
    assert_response :success
  end

  test "should get twiml" do
    get calls_twiml_url
    assert_response :success
  end
end
