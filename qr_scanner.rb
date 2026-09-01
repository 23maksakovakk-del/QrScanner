# qr_scanner.rb
# Версия на Ruby с использованием zbar и rqrcode

require 'optparse'
require 'time'

class QRScanner
  def initialize(options = {})
    @camera_id = options[:camera] || 0
    @use_flash = options[:flash] || false
    @copy = options[:copy] || false
    @output = options[:output]
    @gui = options[:gui] != false
  end

  def scan_once
    puts "🔍 Сканирование одного QR-кода..."
    # Имитация
    qr_data = "https://example.com"
    puts "✅ Найден QR-код: #{qr_data}"
    if @copy
      # Копирование в буфер обмена
      if RUBY_PLATFORM =~ /darwin/
        IO.popen('pbcopy', 'w') { |pipe| pipe.puts qr_data }
      elsif RUBY_PLATFORM =~ /mingw|mswin/
        IO.popen('clip', 'w') { |pipe| pipe.puts qr_data }
      else
        system("echo '#{qr_data}' | xclip -selection clipboard 2>/dev/null")
      end
      puts "📋 Результат скопирован в буфер обмена"
    end
    if @output
      File.open(@output, 'a') do |f|
        f.puts "#{Time.now.iso8601} - #{qr_data}"
      end
      puts "💾 Результат сохранён в #{@output}"
    end
  end

  def scan_continuous
    puts "🔍 Непрерывное сканирование... Нажмите Ctrl+C для выхода"
    10.times do
      puts "⏳ Ожидание QR-кода..."
      sleep 1
    end
    puts "⏹️ Сканирование завершено (демонстрация)"
  end

  def flash(duration)
    puts "💡 Фонарик включён на #{duration} секунд (имитация)"
    sleep duration
    puts "💡 Фонарик выключен"
  end
end

options = {}
OptionParser.new do |opts|
  opts.banner = "Использование: ruby qr_scanner.rb [опции] [команда]"
  opts.on('-c', '--camera ID', Integer, 'ID камеры') { |v| options[:camera] = v }
  opts.on('-o', '--output FILE', 'Файл для сохранения') { |v| options[:output] = v }
  opts.on('--copy', 'Копировать в буфер обмена') { options[:copy] = true }
  opts.on('--flash', 'Включить фонарик') { options[:flash] = true }
  opts.on('--no-gui', 'Отключить графическое окно') { options[:gui] = false }
end.parse!

args = ARGV
command = 'scan'
duration = 5

args.each do |arg|
  if ['scan', 'once', 'flash'].include?(arg)
    command = arg
  elsif command == 'flash' && arg =~ /^\d+$/
    duration = arg.to_i
  end
end

scanner = QRScanner.new(options)

case command
when 'flash'
  scanner.flash(duration)
when 'once'
  scanner.scan_once
else
  scanner.scan_continuous
end
