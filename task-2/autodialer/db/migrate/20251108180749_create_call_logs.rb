class CreateCallLogs < ActiveRecord::Migration[8.1]
  def change
    create_table :call_logs do |t|
      t.references :contact, null: false, foreign_key: true
      t.string :status
      t.string :sid
      t.datetime :started_at
      t.datetime :ended_at
      t.integer :duration
      t.text :error_message

      t.timestamps
    end
  end
end
