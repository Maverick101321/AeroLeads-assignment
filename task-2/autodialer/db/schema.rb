# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[8.1].define(version: 2025_11_22_123624) do
  create_table "blogs", force: :cascade do |t|
    t.text "body"
    t.datetime "created_at", null: false
    t.string "title"
    t.datetime "updated_at", null: false
  end

  create_table "call_logs", force: :cascade do |t|
    t.integer "contact_id", null: false
    t.datetime "created_at", null: false
    t.integer "duration"
    t.datetime "ended_at"
    t.text "error_message"
    t.string "sid"
    t.datetime "started_at"
    t.string "status"
    t.datetime "updated_at", null: false
    t.index ["contact_id"], name: "index_call_logs_on_contact_id"
  end

  create_table "contacts", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.datetime "last_called_at"
    t.string "phone_number"
    t.string "status"
    t.datetime "updated_at", null: false
  end

  add_foreign_key "call_logs", "contacts"
end
