import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Header        from "../../components/layout/Header";
import Navbar        from "../../components/layout/Navbar";
import Sidebar       from "../../components/layout/Sidebar";
import HeroSlider    from "../../components/home/HeroSlider";
import ProductCards  from "../../components/home/ProductCards";
import TodayDeals    from "../../components/home/TodayDeals";
import ReturnModal   from "../../components/returniq/ReturnModal";
import Toast         from "../../components/returniq/Toast";

export default function HomePage() {
  const [sidebarOpen,  setSidebarOpen]  = useState(false);
  const [modalOpen,    setModalOpen]    = useState(false);
  const [toastVisible, setToastVisible] = useState(false);
  const [toastMsg,     setToastMsg]     = useState("");
  const navigate = useNavigate();

  // Listen for agent grading updates
  useEffect(() => {
    function checkNotification() {
      const notifStr = localStorage.getItem("returniq_notification");
      if (notifStr) {
        try {
          const notif = JSON.parse(notifStr);
          if (notif.visible) {
            setToastMsg(notif.message);
            setToastVisible(true);
            // Clear notification
            localStorage.removeItem("returniq_notification");
          }
        } catch (_) {}
      }
    }

    checkNotification();
    const interval = setInterval(checkNotification, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <Header onReturnClick={() => setModalOpen(true)} />
      <Navbar onSidebarOpen={() => setSidebarOpen(true)} />
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <main>
        <HeroSlider onReturnClick={() => setModalOpen(true)} />
        <div className="main">
          <div className="productBackgraound">
            <ProductCards />
          </div>
          <TodayDeals />
        </div>
      </main>

      <ReturnModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onComplete={() => {
          setToastMsg("Your return has been scheduled successfully!");
          setToastVisible(true);
          setModalOpen(false);
          // Redirect to my returns tracker page
          setTimeout(() => {
            navigate("/my-returns");
          }, 1500);
        }}
      />
      <Toast
        message={toastMsg}
        visible={toastVisible}
        onDismiss={() => setToastVisible(false)}
      />
    </>
  );
}
