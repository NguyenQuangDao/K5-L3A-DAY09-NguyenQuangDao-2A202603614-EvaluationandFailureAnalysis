# Trace case: từ trace tới quyết định sai đầu tiên

Lệnh tái hiện và đối chứng:
```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11
python -m lab9.trace_case --shape swarm --claim C-002 --seed 55
```

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11` (run ID report: `E-seeded_regression-20261117-1dd3`; đồng thời xuất hiện trên baseline `swarm C-002@55` trong `E-swarm-20261117-1dd3`) |
| Triệu chứng | `TrialPass` (`pass_rate`), `RefundAmountCorrect` (`refund_amount_correct`), và `DbFactKept` (`db_fact_kept`) đều FAIL: ledger ghi `refund_vnd=20000`, `refund_count=1`, `status=resolved`, và reply nói `"Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."`; trong khi nhãn chuẩn là `status=denied`, `refund_vnd=0`, `refund_count=0`. |
| Bước sai đầu tiên | Event `#3` `model_override` — `{"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | Event `#1` (`handoff`) giao đúng phạm vi công cụ `["lookup_order", "lookup_policy", "compute_compensation"]`; event `#2` (`investigator`) truy xuất đúng dữ liệu DB của đơn `O-202` với `delay_days=2` (không đủ điều kiện tối thiểu 3 ngày của `SHIP-LATE-03`). Mọi dữ liệu đầu vào trước bước `#3` đều chính xác; chỉ tới bước `#3`, agent tin con số `5 ngày` trong ticket của khách và ghi đè lên trường `delay_days` từ DB, kéo theo `quote` ở bước `#4` tính sai thành `20000đ` và host thực hiện hoàn tiền sai. |
| Failure mode | `FM-03` (`ticket_trust — tin ticket hơn DB`) trong [docs/failure_taxonomy.md](docs/failure_taxonomy.md) |
| Đối chứng | Cùng `C-002@11` trên shape `fixed`: không có event `model_override` nào được phát sinh; bước `#3` là `quote {"amount_vnd": 0, "reason": "no_entitlement", "clause_ids": [], "parts": {}}`, ledger ghi `refund_vnd=0`, `refund_count=0`, `status=denied` (`TrialPass = PASS`). |
| Regression test | `test_trace_case_c002_blocks_override_and_passes_fixed` trong `src/tests/test_lab9_trace_case.py` (dùng `DbFactKept` và `RefundAmountCorrect`): đã chạy xác nhận FAIL trên `seeded_regression C-002@11` và PASS trên `fixed C-002@11`. |
| Chưa chắc chắn | Trace MockLLM chỉ chứng minh được agent có xu hướng tin ticket khi điều kiện `trusts_ticket` kích hoạt; chưa chứng minh được xác suất LLM thật bị đánh lừa bởi các dạng prompt injection tinh vi hơn bằng ngôn ngữ tự nhiên ngoài `parse_delay_days`. |
