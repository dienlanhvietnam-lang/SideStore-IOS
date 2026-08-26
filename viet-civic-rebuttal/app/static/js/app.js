(() => {
  const head = document.querySelector(".job-head");
  if (!head) return;

  const jobId = head.dataset.jobId;
  const statusLine = document.getElementById("status-line");
  const statusPill = document.getElementById("status-pill");
  const statusMsg = document.getElementById("status-msg");
  const progressPanel = document.getElementById("progress-panel");
  const resultPanel = document.getElementById("result-panel");
  const vanXoi = document.getElementById("van-xoi");
  const saveHint = document.getElementById("save-hint");

  const statusLabels = {
    queued: "chờ",
    downloading: "tải về",
    extracting: "tách media",
    transcribing: "nhận dạng giọng",
    analyzing: "phân tích",
    done: "xong",
    failed: "lỗi",
  };

  function fillList(id, items) {
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = "";
    (items || []).forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      el.appendChild(li);
    });
  }

  function renderJob(job) {
    statusPill.textContent = statusLabels[job.status] || job.status;
    statusMsg.textContent = job.progress_message || "";
    head.dataset.status = job.status;

    if (progressPanel) {
      progressPanel.hidden = job.status === "done" || job.status === "failed";
    }

    const transcript = document.getElementById("transcript");
    if (transcript) transcript.textContent = job.transcript || "";

    fillList("frame-notes", job.frame_notes || []);

    if (job.error) {
      let err = document.getElementById("error-panel");
      if (!err) {
        err = document.createElement("section");
        err.id = "error-panel";
        err.className = "banner banner-error";
        statusLine.after(err);
      }
      err.innerHTML = `<strong>Không hoàn tất:</strong> ${job.error}`;
    }

    if (job.analysis && resultPanel) {
      resultPanel.hidden = false;
      document.getElementById("tom-tat").textContent = job.analysis.tom_tat_video || "";
      document.getElementById("gia-tri").textContent = job.analysis.gia_tri_cong_dan || "";
      document.getElementById("do-tin-cay").textContent = job.analysis.do_tin_cay || "";
      document.getElementById("che-do").textContent = job.analysis.che_do || "";
      fillList("khang-dinh", job.analysis.cac_khang_dinh);
      fillList("lo-hong", job.analysis.lo_hong_lap_luan);
      fillList("diem-dung", job.analysis.diem_dung_can_thua_nhan);
      fillList("hanh-dong", job.analysis.goi_y_hanh_dong);
      if (vanXoi && document.activeElement !== vanXoi) {
        vanXoi.value = job.analysis.phan_bien_van_xoi || "";
      }
    }
  }

  async function poll() {
    try {
      const res = await fetch(`/api/viec/${jobId}`);
      if (!res.ok) return;
      const job = await res.json();
      renderJob(job);
      if (job.status !== "done" && job.status !== "failed") {
        setTimeout(poll, 1500);
      }
    } catch (_) {
      setTimeout(poll, 2500);
    }
  }

  if (head.dataset.status !== "done" && head.dataset.status !== "failed") {
    poll();
  }

  const btnCopy = document.getElementById("btn-copy");
  const btnSave = document.getElementById("btn-save");

  if (btnCopy && vanXoi) {
    btnCopy.addEventListener("click", async () => {
      await navigator.clipboard.writeText(vanXoi.value);
      saveHint.textContent = "Đã sao chép phản biện văn xuôi.";
    });
  }

  if (btnSave && vanXoi) {
    btnSave.addEventListener("click", async () => {
      const res = await fetch(`/api/viec/${jobId}/cap-nhat-van-xoi`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phan_bien_van_xoi: vanXoi.value }),
      });
      const data = await res.json();
      saveHint.textContent = data.message || data.error || "Xong.";
    });
  }
})();
