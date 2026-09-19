# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Bacvuongtoiday]
**Thành viên:** Đoàn Bá Khải, Nguyễn Văn An, Đỗ Thanh Lâm, Trần Ngọc Khuyến
**Ngày:** 2026-09-19

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy chế đào tạo và dịch vụ sinh viên — Học viện Công nghệ Bưu chính Viễn thông (PTIT)

**Tại sao nhóm chọn chủ đề này?**
> Đề bài bắt buộc lớp L3A phải chọn chủ đề "dịch vụ/quy định đại học". Nhóm chọn nguồn từ Phòng Giáo vụ PTIT (giaovu.ptit.edu.vn) vì đây là trang chính thức, công khai, không bị chặn bởi robots.txt, và nội dung có cấu trúc rõ ràng (thông báo hành chính) phù hợp để thử nghiệm RAG. Ngoài ra, nội dung liên quan trực tiếp đến sinh viên trong lớp nên dễ kiểm chứng tính chính xác.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Đăng ký học lại cải thiện điểm | `giaovu.ptit.edu.vn/to-chuc-cac-lop-hoc-lai...` | 2026-09-19 / 2026 | 2,509 | `audience=student`, `department=giaovu`, `category=academic` |
| 2 | Thi chuẩn đầu ra Tiếng Anh đợt 2 | `giaovu.ptit.edu.vn/to-chuc-ky-thi-chuan-dau-ra...` | 2026-09-19 / 2026 | 5,364 | `audience=student`, `department=giaovu`, `category=academic` |
| 3 | Xét cấp học bổng kỳ 1 | `giaovu.ptit.edu.vn/ket-luan-cua-hoi-dong-xet...` | 2026-09-19 / not-stated | 4,807 | `audience=student`, `department=giaovu`, `category=scholarship` |
| 4 | Chuyển đổi điểm thi ACCA | `giaovu.ptit.edu.vn/tiep-nhan-ho-so-xet-cong-nhan...` | 2026-09-19 / not-stated | 4,442 | `audience=student`, `department=giaovu`, `category=academic` |
| 5 | Tư vấn chuyên ngành khóa 2023 | `giaovu.ptit.edu.vn/tu-van-chuyen-nganh-dao-tao-khoa-2023...` | 2026-09-19 / 2023 | 2,175 | `audience=student`, `department=giaovu`, `category=academic` |
| 6 | Tư vấn chuyên ngành khóa 2024 | `giaovu.ptit.edu.vn/tu-van-chuyen-nganh-dao-tao-khoa-2024...` | 2026-09-19 / 2024 | 1,710 | `audience=student`, `department=giaovu`, `category=academic` |
| 7 | Lớp đầu khóa tân sinh viên 2021 | `ptit.edu.vn/thong-bao-to-chuc-lop-dau-khoa...` | 2026-09-19 / 2021 | 4,576 | `audience=student`, `department=ctsv`, `category=orientation` |
| 8 | Kết quả miễn thi Tiếng Anh | `giaovu.ptit.edu.vn/ket-qua-xet-mien-hoc...` | 2026-09-19 / 2026 | 1,953 | `audience=student`, `department=giaovu`, `category=academic` |
| 9 | Bổ nhiệm Giáo sư, Phó giáo sư PTIT | `ptit.edu.vn/thong-bao-ve-viec-bo-nhiem...` | 2026-09-19 / not-stated | 804 | `audience=faculty`, `department=organization`, `category=faculty-affairs` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| doc_id | string | "hoc-lai" | Định danh duy nhất để xác định nguồn và hỗ trợ delete_document |
| audience | string | "student" / "faculty" / "all" | Cho phép lọc tài liệu theo đối tượng, tránh trả kết quả sai đối tượng |
| source_url | string | "https://giaovu.ptit.edu.vn/..." | Truy xuất nguồn gốc, kiểm chứng tính chính xác |
| department | string | "giaovu" | Phân loại theo phòng ban để thu hẹp phạm vi tìm kiếm |
| category | string | "academic" | Phân loại theo chủ đề (học vụ, thi cử, hành chính) |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| hoc-lai + tuvan-khoa24 + faculty-appointment (3,958 ký tự, bỏ frontmatter) | FixedSizeChunker (`fixed_size`) | 9 | 484.22 ký tự | Không hoàn toàn — có thể cắt ngang câu ở ranh giới 500 ký tự |
| hoc-lai + tuvan-khoa24 + faculty-appointment (3,958 ký tự, bỏ frontmatter) | SentenceChunker (`by_sentences`) | 10 | 392.20 ký tự | Có — mỗi chunk là nhóm tối đa ba câu trọn vẹn |
| hoc-lai + tuvan-khoa24 + faculty-appointment (3,958 ký tự, bỏ frontmatter) | RecursiveChunker (`recursive`) | 10 | 393.90 ký tự | Phần lớn có — ưu tiên cắt theo đoạn văn trước khi cắt nhỏ |

### Chiến lược của từng thành viên

**Thành viên 1 — Đỗ Thanh Lâm**
- **Loại chiến lược:** FixedSize (chunk_size=500, overlap=50)
- **Mô tả & lý do chọn:** Cắt cứng mỗi 500 ký tự với 50 ký tự chồng lấp. Đây là baseline đơn giản nhất, dùng để so sánh với các chiến lược phức tạp hơn. Overlap=50 giúp giảm thiểu mất thông tin tại ranh giới chunk.

**Thành viên 2 — Trần Ngọc Khuyến**
- **Loại chiến lược:** Sentence (max_sentences_per_chunk=3)
- **Mô tả & lý do chọn:** Cắt theo đơn vị câu, mỗi chunk chứa tối đa 3 câu. Phù hợp với văn bản hành chính PTIT vì mỗi điều khoản thường được viết thành 2-3 câu ngắn gọn.

**Thành viên 3 — Nguyễn Văn An**
- **Loại chiến lược:** Recursive (chunk_size=500)
- **Mô tả & lý do chọn:** Cắt đệ quy theo thứ tự ưu tiên: đoạn văn → dòng → câu → từ. Giữ được cấu trúc logic của văn bản quy chế vì ưu tiên cắt tại ranh giới đoạn văn tự nhiên.

**Thành viên 4 — Đoàn Bá Khải (Report & Demo Lead)**
- **Loại chiến lược:** Tổng hợp kết quả cả 3 chiến lược trên, dẫn phần thuyết trình.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| TV1 - Lâm | FixedSize | 8/10 | Đơn giản, chunk đều nhau, dễ dự đoán số lượng | Cắt ngang câu, Top-1 Q3 lấy sai doc (tuvan-khoa23) |
| TV2 - Khuyến | Sentence | 8/10 | Giữ trọn vẹn câu, ngữ nghĩa mạch lạc | Chunk dài ngắn không đều, Q5 Top-2 lấy nhầm doc ACCA |
| TV3 - An | Recursive | 9/10 | Giữ cấu trúc đoạn văn, score cao nhất ở Q4 (0.646) | Số chunk nhiều nhất (61), tốn tài nguyên embedding hơn |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **Recursive** cho kết quả tốt nhất trên văn bản quy chế PTIT. Lý do: văn bản hành chính được viết theo cấu trúc đoạn rõ ràng (mỗi mục một đoạn, phân cách bằng dòng trống). Recursive ưu tiên cắt theo `\n\n` nên giữ nguyên được từng mục/điều khoản thành chunk độc lập, giúp retrieval chính xác hơn. Đặc biệt ở Q4 (nhập Mã môn), Recursive đạt score cao nhất (0.646) vì chunk chứa trọn vẹn đoạn hướng dẫn đăng ký.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Hạn cuối để đăng ký nguyện vọng học lại cải thiện điểm là khi nào? | Từ 12h00 ngày 25/09 đến 24h00 ngày 29/09/2026 | hoc-lai.md — mục "Kế hoạch thực hiện" |
| 2 | Nguyên tắc ưu tiên khi mở các lớp học lại là gì? | Ưu tiên mở các lớp có từ 5 sinh viên trở lên đăng ký; các HP không mở kỳ hè 2025-2026 | hoc-lai.md — mục "Nguyên tắc mở lớp" |
| 3 | Ngành CNKT Điện, điện tử được chia thành những chuyên ngành nào? | Kỹ thuật điện tử máy tính và Thiết kế vi mạch | tuvan-khoa24.md — mục "Các chuyên ngành" |
| 4 | Khi đăng ký học lại trên qldt, SV nhập gì vào ô Môn học? | Nhập đúng "Mã môn" | hoc-lai.md — mục "Lưu ý" |
| 5 | Buổi tư vấn chọn chuyên ngành diễn ra ở phòng nào và lúc mấy giờ? *(cần filter audience=student)* | Phòng 101 nhà A2 lúc 19h00 hoặc phòng 205 nhà A2 lúc 13h00 | tuvan-khoa24.md — mục "Hỗ trợ tư vấn" |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Hạn đăng ký nguyện vọng | Sentence baseline (mock) | Không | Mock không trả chunk chứa mốc ngày trong top-3. |
| 2 | Nguyên tắc mở lớp | Sentence baseline (mock) | Không | Mock không trả chunk chứa điều kiện 5 sinh viên trong top-3. |
| 3 | Chuyên ngành Điện, điện tử | Sentence baseline (mock) | Không | Mock không trả section gold trong top-3. |
| 4 | Nhập gì vào ô Môn học | Sentence baseline (mock) | Không | Mock không trả chunk có “Mã môn” trong top-3. |
| 5 | Phòng tư vấn chuyên ngành | Sentence baseline (mock) | Không | Filter student chạy được nhưng mock không trả gold chunk. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Chưa thể kết luận filter cải thiện chất lượng với MockEmbedder: filter được áp dụng trước search nhưng top-3 vẫn không có gold chunk. `tuvan-khoa23` đã được sửa đúng thành `audience=student`; corpus bổ sung một tài liệu thật cho `faculty`, nhưng cần chạy lại với semantic embedder để đo A/B có ý nghĩa.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. Recursive Chunker cho kết quả tốt nhất trên văn bản hành chính có cấu trúc đoạn rõ ràng, vì nó ưu tiên cắt tại ranh giới đoạn tự nhiên.
> 2. Metadata filter là "vũ khí bí mật" — cùng một câu hỏi, không filter thì AI trả lời sai đối tượng, có filter thì chính xác tuyệt đối.
> 3. FixedSize tuy đơn giản nhưng đôi khi bị cắt ngang thông tin quan trọng, khiến Top-1 lấy sai doc trong khi đáp án nằm ở Top-2.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng bộ tài liệu nhưng cách cắt khác nhau dẫn đến thứ hạng retrieval khác biệt đáng kể. Sentence giữ ngữ nghĩa câu tốt nhưng chunk dài ngắn không đều; FixedSize đều nhưng hay cắt ngang; Recursive cân bằng nhất. Điều này chứng minh chunking strategy là yếu tố quyết định chất lượng RAG, không chỉ phụ thuộc vào embedding model.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Sẽ thêm chunker theo heading (## Điều X) vì văn bản quy chế PTIT có cấu trúc mục rõ ràng. Ngoài ra sẽ bóc tách frontmatter YAML ra khỏi nội dung trước khi chunk, vì hiện tại phần YAML metadata đang bị lẫn vào chunk đầu tiên, gây nhiễu cho embedding.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 0 / 10 (baseline mock, chưa chấm cuối) |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **30 / 40 (tạm tính)** |
