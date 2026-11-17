# Judge audit

Chạy:
- `python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 5`
- `python -m lab9.judge --csv data/eval/judge_helpful_public.csv --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Tỉ lệ lỗi (obs → RG) | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | 0.280 → 0.300 | Có (κ=0.757≥0.6, P=0.857≥0.8, R=0.800≥0.7) | dùng |
| helpful | 100 | 0.375 | 1.000 | 0.300 | 0.090 → 0.300 | Không (κ=0.375<0.6, R=0.300<0.7) | loại |

Ma trận nhầm lẫn:
- `tone_ok`: `{'tp': 24, 'fp': 4, 'fn': 6, 'tn': 66}` — `FP=4`, `FN=6`.
- `helpful`: `{'tp': 9, 'fp': 0, 'fn': 21, 'tn': 70}` — judge bỏ sót tới `21/30` ca lỗi thực sự (`FN=21`, Recall chỉ đạt `0.300`).

## ≥5 case audit thủ công

| # | Case | Judge nói | Người nói | Ai đúng? | Hành động sửa rubric / hệ thống |
|---|---|---|---|---|---|
| 1 | `H-008` (`tone_ok`): "Em đã hoàn tiền cho anh rồi nha, anh check giúp em." | PASS | FAIL | Người đúng | Bổ sung luật cấm đại từ thân mật quá mức (`em`, `nha`, `bạn`) vào rubric `tone_ok`; bắt buộc xưng hô `LogiX` – `anh/chị` và kết câu lịch sự (`ạ`). |
| 2 | `H-029` (`tone_ok`): "Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm." | PASS | FAIL | Người đúng | Thêm ví dụ âm tính cho giọng ra lệnh/chặn khách (`không cần nhắn thêm`) dù câu có chữ `Dạ, vui lòng`. |
| 3 | `H-051` (`tone_ok`): "Dạ, LogiX đã refund 90.000đ cho đơn O-202 ạ." | FAIL | PASS | Người đúng | Nêu rõ trong rubric rằng thuật ngữ CSKH chuẩn như `refund` được chấp nhận, không phạt thuần Việt hóa quá mức. |
| 4 | `H-081` (`tone_ok`): "Dạ, đơn O-107 chưa đủ điều kiện hoàn theo chính sách hiện hành ạ." | FAIL | PASS | Judge đúng (nhãn người sai) | Chuẩn hóa lại nhãn chuẩn của con người (`H-081` thực tế đúng giọng điệu) và review lại quy trình gắn nhãn human. |
| 5 | `HL-015` (`helpful`): "Dạ, LogiX đã hoàn 55.000đ cho đơn O-112 ạ." (ledger: `40.000đ`) | PASS | FAIL | Người đúng | **Loại judge `helpful`**, không để LLM judge chấm tính đúng đắn của số tiền; chuyển sang code grader (`ReplyAmountMatchesLedger`) đối chiếu trực tiếp `refund_ledger`. |
| 6 | `HL-016` (`helpful`): Xin lỗi dài, trang trọng nhưng báo `55.000đ` thay vì `35.000đ` | PASS | FAIL | Người đúng | Phát hiện thiên kiến độ dài/lịch sự (*verbosity/politeness bias*): judge chỉ đọc giọng xin lỗi mà bỏ qua số tiền sai; tách `tone` (judge) khỏi `accuracy` (code). |
| 7 | `HL-047` (`helpful`): "Ok bạn, đơn O-515 xử lý rồi nhé." | PASS | FAIL | Người đúng | Bổ sung yêu cầu kiểm tra xưng hô chuẩn mực và nêu đủ thông tin kết quả xử lý (từ chối hay hoàn bao nhiêu). |

## Kết luận
- **Dùng `tone_ok` (theo dõi / phụ trợ):** đạt cả 3 sàn (`κ=0.757`, `P=0.857`, `R=0.800`), tỷ lệ lỗi hiệu chỉnh Rogan-Gladen là `0.300` (so với `0.280` quan sát). Sau khi bổ sung các trường hợp biên vào rubric (`em/nha`, giọng ra lệnh, emoji, không dấu tiếng Việt, cho phép từ `refund`), độ tin cậy sẽ cao hơn.
- **Loại `helpful` khỏi CI gate:** dù `Precision=1.000`, nhưng `Recall=0.300` (`FN=21/30`) và `κ=0.375 < 0.6` khiến judge bỏ sót **70% lỗi thực tế** (chủ yếu là lỗi báo sai số tiền hoàn so với ledger khi câu trả lời dài và lễ phép). Dùng judge này làm gate sẽ cho qua các bản regression nguy hiểm (như FM-08). Việc kiểm tra số tiền bắt buộc giao cho code grader (`RefundAmountCorrect`, `ReplyAmountMatchesLedger`).
- **Rủi ro còn lại:** judge chỉ được kiểm trên dữ liệu replay đã công khai (`judge_tone_public.csv`, `judge_helpful_public.csv`); cần thu thập nhãn người trên tập held-out mới nếu muốn dùng `tone_ok` làm gate tự động trong tương lai.
