import React, { useState, useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { X, ArrowRight, ChevronRight, CheckCircle2, Play, MousePointer2, Image as ImageIcon, Video, Building2, Eye, LineChart, MessageCircle } from 'lucide-react';
import logoImg from './assets/logo.png';

gsap.registerPlugin(ScrollTrigger);

// 🔗 Cole aqui a URL do seu Google Apps Script (Web App)
// Siga o guia em google_apps_script.md para configurar
const GOOGLE_SHEETS_URL = 'https://script.google.com/macros/s/AKfycbzJAhFx-uww8Q0b7_6TF25nTRDmKXR2MPuRiefOdrw2GF2jZ7zKiMkay2Xym6s45crG/exec';

// --- Componente: Botão Magnético ---
const MagneticButton = ({ children, onClick, className = '' }) => {
  const btnRef = useRef(null);

  useEffect(() => {
    const btn = btnRef.current;
    if (!btn) return;

    const ctx = gsap.context(() => {
      btn.addEventListener('mouseenter', () => {
        gsap.to(btn, { scale: 1.03, duration: 0.3, ease: 'power2.out' });
        gsap.to(btn, { y: -2, duration: 0.3, ease: 'power2.out' });
      });
      btn.addEventListener('mouseleave', () => {
        gsap.to(btn, { scale: 1, duration: 0.3, ease: 'power2.out' });
        gsap.to(btn, { y: 0, duration: 0.3, ease: 'power2.out' });
      });
    }, btn);

    return () => ctx.revert();
  }, []);

  return (
    <button
      ref={btnRef}
      onClick={onClick}
      className={`relative overflow-hidden inline-flex items-center justify-center font-sans font-semibold tracking-wide transition-all ${className}`}
    >
      <span className="relative z-10 flex items-center gap-2">{children}</span>
    </button>
  );
};

// --- Componente: Modal de Orçamento (Multi-Step) ---
const OrcamentoModal = ({ isOpen, onClose }) => {
  const modalRef = useRef(null);
  const bgRef = useRef(null);
  
  const [step, setStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [formData, setFormData] = useState({
    serviceType: '', // 'image' | 'video'
    has3dFile: '',
    resolution: '',
    imageCount: '',
    videoType: '',
    videoDuration: '',
    deadline: '',
    firstName: '',
    lastName: '',
    email: '',
    whatsapp: '',
  });

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      gsap.fromTo(bgRef.current, { opacity: 0 }, { opacity: 1, duration: 0.4, ease: 'power3.out' });
      gsap.fromTo(modalRef.current, { y: 50, opacity: 0, scale: 0.95 }, { y: 0, opacity: 1, scale: 1, duration: 0.5, ease: 'power3.out', delay: 0.1 });
    } else {
      document.body.style.overflow = 'auto';
      setStep(1); // reset on close
      setIsSubmitting(false);
      setSubmitError('');
      setFormData({
        serviceType: '', has3dFile: '', resolution: '', imageCount: '', videoType: '', videoDuration: '', deadline: '', firstName: '', lastName: '', email: '', whatsapp: ''
      });
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleNext = () => {
    if (step === 1 && formData.serviceType === 'image') setStep('2A');
    else if (step === 1 && formData.serviceType === 'video') setStep('2B');
    else if (step === '2A' || step === '2B') setStep(3);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitError('');

    try {
      // Monta o payload com timestamp
      const payload = {
        ...formData,
        timestamp: new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' }),
      };

      // IMPORTANTE: com mode: 'no-cors', apenas 'text/plain' funciona
      // O Google Apps Script lê via e.postData.contents e faz JSON.parse()
      await fetch(GOOGLE_SHEETS_URL, {
        method: 'POST',
        mode: 'no-cors',
        headers: { 'Content-Type': 'text/plain;charset=utf-8' },
        body: JSON.stringify(payload),
      });

      // mode: 'no-cors' retorna opaque response (status 0), não há como checar sucesso
      console.log('✅ Dados enviados para o Google Sheets:', payload);
      setStep('Success');
    } catch (error) {
      console.error('❌ Erro ao enviar:', error);
      setSubmitError('Erro ao enviar. Tente novamente.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStep = () => {
    if (step === 1) {
      return (
        <div className="space-y-6">
          <h3 className="font-drama text-3xl font-semibold mb-2">O que você busca criar?</h3>
          <p className="text-ivory/60 mb-6 font-sans">Selecione o tipo de visualização que melhor atende ao seu projeto.</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button 
              onClick={() => setFormData({ ...formData, serviceType: 'image' })}
              className={`p-6 rounded-[1.5rem] border text-left transition-all duration-300 ${formData.serviceType === 'image' ? 'border-accent bg-accent/10' : 'border-slate bg-primary hover:border-ivory/30'}`}
            >
              <div className="w-12 h-12 bg-slate rounded-full flex items-center justify-center mb-4">
                <ImageIcon className="text-ivory w-6 h-6" />
              </div>
              <h4 className="font-sans font-bold text-lg mb-1">Renderização de Imagem</h4>
              <p className="text-sm text-ivory/60">Fotorrealismo perfeito para stands, catálogos e anúncios.</p>
            </button>
            <button 
              onClick={() => setFormData({ ...formData, serviceType: 'video' })}
              className={`p-6 rounded-[1.5rem] border text-left transition-all duration-300 ${formData.serviceType === 'video' ? 'border-accent bg-accent/10' : 'border-slate bg-primary hover:border-ivory/30'}`}
            >
              <div className="w-12 h-12 bg-slate rounded-full flex items-center justify-center mb-4">
                <Video className="text-ivory w-6 h-6" />
              </div>
              <h4 className="font-sans font-bold text-lg mb-1">Vídeo Cinematográfico</h4>
              <p className="text-sm text-ivory/60">Animações hollywoodianas para engajamento e lançamentos.</p>
            </button>
          </div>
          
          <div className="flex justify-end mt-8">
            <MagneticButton onClick={handleNext} className="bg-accent text-primary px-8 py-3 rounded-[2rem] disabled:opacity-50">
              Próximo Passo <ArrowRight className="w-4 h-4 ml-1" />
            </MagneticButton>
          </div>
        </div>
      );
    }

    if (step === '2A' || step === '2B') {
      const isVideo = step === '2B';
      return (
        <div className="space-y-6">
          <h3 className="font-drama text-3xl font-semibold mb-2">Detalhes Técnicos</h3>
          <p className="text-ivory/60 mb-6 font-sans">Isso nos ajuda a precificar corretamente e definir prazos.</p>
          
          <div className="space-y-5">
            <div>
              <label className="block text-sm font-semibold mb-2">Você já possui o modelo 3D? (Sketchup, Revit, etc)</label>
              <div className="flex gap-4">
                {['Sim', 'Não'].map(opt => (
                  <button key={opt} onClick={() => setFormData({...formData, has3dFile: opt})} className={`px-6 py-3 rounded-xl border flex-1 transition-all ${formData.has3dFile === opt ? 'border-accent bg-accent/10' : 'border-slate hover:bg-slate'}`}>
                    {opt}
                  </button>
                ))}
              </div>
            </div>

            {isVideo ? (
              <>
              <div>
                <label className="block text-sm font-semibold mb-2">Qual é o foco principal do vídeo?</label>
                <div className="flex flex-col gap-2">
                  {['Institucional da Construtora', 'Lançamento Imobiliário', 'Passeio por Ambientes (Tour)'].map(opt => (
                    <button key={opt} onClick={() => setFormData({...formData, videoType: opt})} className={`px-4 py-3 rounded-xl border text-left transition-all ${formData.videoType === opt ? 'border-accent bg-accent/10' : 'border-slate hover:bg-slate'}`}>
                      {opt}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Duração estimada do vídeo</label>
                <div className="grid grid-cols-3 gap-2">
                  {['0 a 15s', '15 a 30s', '30 a 45s', '45 a 60s', '60 a 90s', 'Acima de 90s'].map(opt => (
                    <button key={opt} onClick={() => setFormData({...formData, videoDuration: opt})} className={`px-3 py-3 rounded-xl border text-center text-sm transition-all ${formData.videoDuration === opt ? 'border-accent bg-accent/10 text-accent font-semibold' : 'border-slate hover:bg-slate'}`}>
                      {opt}
                    </button>
                  ))}
                </div>
              </div>
              </>
            ) : (
              <>
              <div>
                <label className="block text-sm font-semibold mb-2">Resolução desejada</label>
                <div className="flex flex-col gap-2">
                  {['Padrão (4K)', 'Premium (8K para outdoors)'].map(opt => (
                    <button key={opt} onClick={() => setFormData({...formData, resolution: opt})} className={`px-4 py-3 rounded-xl border text-left transition-all ${formData.resolution === opt ? 'border-accent bg-accent/10' : 'border-slate hover:bg-slate'}`}>
                      {opt}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Quantas imagens serão necessárias?</label>
                <div className="grid grid-cols-3 gap-2">
                  {['1', '2 a 3', '4 a 6', '7 a 10', '11 a 20', 'Mais de 20'].map(opt => (
                    <button key={opt} onClick={() => setFormData({...formData, imageCount: opt})} className={`px-3 py-3 rounded-xl border text-center text-sm transition-all ${formData.imageCount === opt ? 'border-accent bg-accent/10 text-accent font-semibold' : 'border-slate hover:bg-slate'}`}>
                      {opt}
                    </button>
                  ))}
                </div>
              </div>
              </>
            )}

            <div>
               <label className="block text-sm font-semibold mb-2">Prazo ideal para entrega</label>
               <select 
                 value={formData.deadline} 
                 onChange={(e) => setFormData({...formData, deadline: e.target.value})}
                 className="w-full bg-slate border border-slate rounded-xl p-3 text-ivory outline-none focus:border-accent"
               >
                 <option value="" disabled>Selecione uma base...</option>
                 <option value="Urgente (1 semana)">Urgente (até 7 dias) - Sujeito a taxa de aceleração</option>
                 <option value="Médio (2 a 3 semanas)">Médio (15 a 21 dias)</option>
                 <option value="Longo (Mais de 1 mês)">Longo (Mais de 30 dias)</option>
               </select>
            </div>
          </div>
          
          <div className="flex justify-between mt-8">
            <button onClick={() => setStep(1)} className="text-ivory/60 hover:text-ivory px-4 py-2">Voltar</button>
            <MagneticButton onClick={handleNext} className="bg-accent text-primary px-8 py-3 rounded-[2rem]">
              Próximo Passo <ArrowRight className="w-4 h-4 ml-1" />
            </MagneticButton>
          </div>
        </div>
      )
    }

    if (step === 3) {
      return (
        <form onSubmit={handleSubmit} className="space-y-6">
          <h3 className="font-drama text-3xl font-semibold mb-2">Quase lá!</h3>
          <p className="text-ivory/60 mb-6 font-sans">Para onde enviaremos o seu orçamento exclusivo?</p>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-ivory/60 mb-1">Nome</label>
                <input required type="text" value={formData.firstName} onChange={(e) => setFormData({...formData, firstName: e.target.value})} className="w-full bg-slate rounded-lg p-3 text-ivory outline-none focus:border focus:border-accent/40" placeholder="Seu nome" />
              </div>
              <div>
                <label className="block text-xs text-ivory/60 mb-1">Sobrenome</label>
                <input required type="text" value={formData.lastName} onChange={(e) => setFormData({...formData, lastName: e.target.value})} className="w-full bg-slate rounded-lg p-3 text-ivory outline-none focus:border focus:border-accent/40" placeholder="Seu sobrenome" />
              </div>
            </div>
            <div>
              <label className="block text-xs text-ivory/60 mb-1">E-mail corporativo</label>
              <input required type="email" value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})} className="w-full bg-slate rounded-lg p-3 text-ivory outline-none focus:border focus:border-accent/40" placeholder="voce@empresa.com" />
            </div>
            <div>
              <label className="block text-xs text-ivory/60 mb-1">WhatsApp</label>
              <input required type="tel" value={formData.whatsapp} onChange={(e) => setFormData({...formData, whatsapp: e.target.value})} className="w-full bg-slate rounded-lg p-3 text-ivory outline-none focus:border focus:border-accent/40" placeholder="(11) 99999-9999" />
            </div>
          </div>
          
          {submitError && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3 text-red-400 text-sm text-center">
              {submitError}
            </div>
          )}

          <div className="flex justify-between mt-8">
            <button type="button" onClick={() => setStep(formData.serviceType === 'image' ? '2A' : '2B')} className="text-ivory/60 hover:text-ivory px-4 py-2" disabled={isSubmitting}>Voltar</button>
            <MagneticButton className={`bg-accent text-primary px-8 py-3 rounded-[2rem] font-bold ${isSubmitting ? 'opacity-60 pointer-events-none' : ''}`}>
              {isSubmitting ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                  Enviando...
                </span>
              ) : 'Solicitar Orçamento'}
            </MagneticButton>
          </div>
        </form>
      );
    }

    if (step === 'Success') {
      return (
        <div className="text-center py-10 space-y-4">
          <CheckCircle2 className="w-16 h-16 text-accent mx-auto mb-4" />
          <h3 className="font-drama text-3xl font-semibold text-accent">Análise em Andamento.</h3>
          <p className="font-sans text-ivory/80 max-w-[300px] mx-auto">Recebemos seus dados. Nossa equipe elaborará uma proposta comercial com estratégia hollywoodiana para o seu projeto.</p>
          <div className="pt-6">
            <button onClick={onClose} className="border border-slate px-6 py-2 rounded-full text-sm hover:bg-slate transition-all">
              Fechar janela
            </button>
          </div>
        </div>
      );
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div ref={bgRef} onClick={onClose} className="absolute inset-0 bg-primary/80 backdrop-blur-md"></div>
      <div 
        ref={modalRef} 
        className="relative bg-primary border-t border-slate border-l border-r rounded-[2.5rem] w-full max-w-xl p-8 shadow-2xl overflow-hidden"
      >
        <button onClick={onClose} className="absolute top-6 right-6 text-ivory/50 hover:text-ivory bg-slate/40 p-2 rounded-full transition-colors">
          <X className="w-5 h-5" />
        </button>

        {/* Header Steps */}
        {step !== 'Success' && (
          <div className="flex gap-2 mb-8">
            <div className={`h-1 flex-1 rounded-full ${step >= 1 ? 'bg-accent' : 'bg-slate'}`}></div>
            <div className={`h-1 flex-1 rounded-full ${step === '2A' || step === '2B' || step === 3 ? 'bg-accent' : 'bg-slate'}`}></div>
            <div className={`h-1 flex-1 rounded-full ${step === 3 ? 'bg-accent' : 'bg-slate'}`}></div>
          </div>
        )}

        <div className="relative z-10">
          {renderStep()}
        </div>
      </div>
    </div>
  );
};

// --- Navbar ---
const Navbar = ({ onOpenModal }) => {
  const navRef = useRef(null);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const trigger = ScrollTrigger.create({
      start: 'top -50',
      end: 99999,
      toggleClass: {className: 'bg-primary/70 backdrop-blur-xl border-slate', targets: navRef.current},
    });
    return () => trigger.kill();
  }, []);

  return (
    <>
      <nav ref={navRef} className="fixed top-4 md:top-6 left-1/2 -translate-x-1/2 z-50 px-4 md:px-8 py-3 md:py-4 rounded-full border border-transparent transition-all duration-500 w-[95%] md:w-[90%] max-w-5xl flex justify-between items-center text-sm font-mono font-medium">
        <div className="flex items-center cursor-pointer hover:scale-[1.03] hover:drop-shadow-xl transition-all duration-300">
          <img src={logoImg} alt="Conrado 3D Studio" className="h-7 md:h-10 w-auto object-contain pointer-events-none" />
        </div>
        <div className="hidden md:flex gap-8">
          <a href="#features" className="hover:text-accent transition-colors">Vantagens</a>
          <a href="#portfolio" className="hover:text-accent transition-colors">Portfólio</a>
          <a href="#protocol" className="hover:text-accent transition-colors">Protocolo</a>
        </div>
        <div className="flex items-center gap-3">
          <MagneticButton onClick={onOpenModal} className="bg-ivory text-primary px-4 md:px-5 py-2 rounded-full text-[10px] md:text-xs font-bold hover:bg-accent hover:text-primary transition-colors">
            Orçamento
          </MagneticButton>
          {/* Hamburger Mobile */}
          <button className="md:hidden flex flex-col gap-1.5 p-2" onClick={() => setMenuOpen(!menuOpen)} aria-label="Menu">
            <span className={`w-5 h-0.5 bg-ivory rounded transition-all duration-300 ${menuOpen ? 'rotate-45 translate-y-2' : ''}`} />
            <span className={`w-5 h-0.5 bg-ivory rounded transition-all duration-300 ${menuOpen ? 'opacity-0' : ''}`} />
            <span className={`w-5 h-0.5 bg-ivory rounded transition-all duration-300 ${menuOpen ? '-rotate-45 -translate-y-2' : ''}`} />
          </button>
        </div>
      </nav>
      {/* Mobile Menu Overlay */}
      {menuOpen && (
        <div className="fixed inset-0 z-40 bg-primary/95 backdrop-blur-2xl flex flex-col items-center justify-center gap-10 md:hidden" onClick={() => setMenuOpen(false)}>
          <a href="#features" className="font-drama italic text-4xl text-ivory hover:text-accent transition-colors">Vantagens</a>
          <a href="#portfolio" className="font-drama italic text-4xl text-ivory hover:text-accent transition-colors">Portfólio</a>
          <a href="#protocol" className="font-drama italic text-4xl text-ivory hover:text-accent transition-colors">Protocolo</a>
          <MagneticButton onClick={() => { setMenuOpen(false); onOpenModal(); }} className="bg-accent text-primary px-10 py-4 rounded-[3rem] text-lg mt-6">
            Solicitar Orçamento
          </MagneticButton>
        </div>
      )}
    </>
  );
};

// --- Cards Interativos das Features ---
const DiagnosticShuffler = () => {
  const [active, setActive] = useState(0);
  const cards = ["Apresentações Imediatas", "Materiais Altamente Fotorrealistas", "Foco Extremo em Vendas"];
  
  useEffect(() => {
    const timer = setInterval(() => {
      setActive(p => (p + 1) % cards.length);
    }, 2500);
    return () => clearInterval(timer);
  }, [cards.length]);

  return (
    <div className="bg-slate p-8 rounded-[2rem] border border-slate/50 flex flex-col h-full shadow-magnetic overflow-hidden relative">
      <h3 className="font-sans font-bold text-2xl mb-2 text-ivory">Imersão Absoluta</h3>
      <p className="text-ivory/60 text-sm mb-8 leading-relaxed">Experiências visuais indescritíveis que encantam investidores antes da primeira fundação.</p>
      <div className="flex-1 relative mt-[60px] h-[150px]">
        {cards.map((text, i) => {
          const isActive = i === active;
          const isNext = i === (active + 1) % cards.length;
          return (
            <div 
              key={text} 
              className={`absolute bottom-0 w-full left-0 bg-primary border text-center border-slate rounded-2xl p-4 transition-all duration-700 ease-[cubic-bezier(0.34,1.56,0.64,1)]`}
              style={{
                transform: isActive ? 'translateY(0) scale(1)' : isNext ? 'translateY(20px) scale(0.95)' : 'translateY(40px) scale(0.9)',
                opacity: isActive ? 1 : isNext ? 0.6 : 0.3,
                zIndex: isActive ? 10 : isNext ? 9 : 8
              }}
            >
              <p className="font-mono text-xs">{text}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const TelemetryTypewriter = () => {
  const [text, setText] = useState('');
  const fullText = "RENDERING...> Elevando a percepção de luxo e o valor de mercado. Autoridade estabelecida através do Pixel Perfect.";
  
  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      setText(fullText.substring(0, i));
      i++;
      if (i > fullText.length) {
        clearInterval(interval);
      }
    }, 50);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate p-8 rounded-[2rem] border border-slate/50 flex flex-col h-full shadow-magnetic">
      <div className="flex items-center gap-2 mb-6">
        <div className="w-2 h-2 rounded-full bg-accent animate-pulse"></div>
        <span className="font-mono text-[10px] text-ivory/40 tracking-widest uppercase">Live Feed</span>
      </div>
      <h3 className="font-sans font-bold text-2xl mb-2 text-ivory">Destaque de Mercado</h3>
      <p className="text-ivory/60 text-sm mb-6 leading-relaxed">Renderizações de padrão absoluto que esmagam a concorrência e valorizam seu imóvel instantaneamente.</p>
      <div className="mt-auto bg-primary border border-slate rounded-xl p-4 min-h-[100px] flex items-end">
         <p className="font-mono text-sm text-accent w-full leading-relaxed">
           {text}<span className="inline-block w-1.5 h-4 ml-1 bg-accent animate-pulse"></span>
         </p>
      </div>
    </div>
  );
};

const CursorProtocolScheduler = () => {
  const containerRef = useRef(null);
  
  useEffect(() => {
    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ repeat: -1, yoyo: true });
      tl.to('.cursor-svg', { x: 50, y: 30, duration: 1, ease: 'power2.inOut' })
        .to('.cursor-svg', { scale: 0.8, duration: 0.1, yoyo: true, repeat: 1 })
        .to('.cell-target', { backgroundColor: '#C9A84C', color: '#000', duration: 0.2 }, '-=0.1')
        .to('.cursor-svg', { x: 120, y: -20, duration: 1, delay: 0.5, ease: 'power2.inOut' });
    }, containerRef);
    return () => ctx.revert();
  }, []);

  return (
    <div ref={containerRef} className="bg-slate p-8 rounded-[2rem] border border-slate/50 flex flex-col h-full shadow-magnetic relative overflow-hidden">
      <h3 className="font-sans font-bold text-2xl mb-2 text-ivory">Conversão Cinematográfica</h3>
      <p className="text-ivory/60 text-sm mb-8 leading-relaxed">Diga adeus as objeções. Nossos renders são desenvolvidos estritamente para acelerar o fechamento.</p>
      <div className="grid grid-cols-7 gap-1 mt-auto relative">
         <MousePointer2 className="cursor-svg text-accent absolute top-[-30px] left-0 w-6 h-6 z-20" />
         {['D','S','T','Q','Q','S','S'].map((dia, i) => (
           <div key={i} className={`h-8 border border-ivory/10 rounded flex items-center justify-center font-mono text-[10px] ${i === 3 ? 'cell-target' : ''}`}>
             {dia}
           </div>
         ))}
      </div>
    </div>
  );
};

// --- Componente: Portfólio Cinematográfico ---
const CinematicPortfolio = () => {
  const containerRef = useRef(null);
  const scrollRef = useRef(null);
  
  // Placeholders de demonstração (substitua pelos seus renders reais na pasta src/assets/portfolio/)
  const placeholderItems = [
    { url: 'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?q=80&w=2075&auto=format&fit=crop', type: 'image', name: 'RESIDENCIAL AURORA' },
    { url: 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?q=80&w=2053&auto=format&fit=crop', type: 'image', name: 'VILLA CHAMPAGNE' },
    { url: 'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?q=80&w=1974&auto=format&fit=crop', type: 'image', name: 'EDIFÍCIO MONARCA' },
    { url: 'https://images.unsplash.com/photo-1613490493576-7fde63acd811?q=80&w=2071&auto=format&fit=crop', type: 'image', name: 'MANSÃO IMPERIAL' },
    { url: 'https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?q=80&w=2053&auto=format&fit=crop', type: 'image', name: 'INTERIOR PRESTIGE' },
  ];

  // Leitura automática do Vite: Puxa dinamicamente TUDO que for jogado dentro da pasta portfolio!
  const portfolioModules = import.meta.glob('./assets/portfolio/*.{png,jpg,jpeg,webp,mp4}', { eager: true, query: '?url', import: 'default' });
  const localItems = Object.keys(portfolioModules).map(key => ({
    url: portfolioModules[key],
    type: key.match(/\.(mp4|webm)$/i) ? 'video' : 'image',
    name: key.split('/').pop().split('.')[0].replace(/_/g, ' ').toUpperCase()
  }));

  // Se tiver arquivos locais, usa eles. Senão, usa os placeholders.
  const items = localItems.length > 0 ? localItems : placeholderItems;

  useEffect(() => {
    if (!scrollRef.current || !containerRef.current) return;
    const ctx = gsap.context(() => {
      const scrollWidth = scrollRef.current.scrollWidth - window.innerWidth;
      
      gsap.to(scrollRef.current, {
        x: -scrollWidth,
        ease: 'none',
        scrollTrigger: {
          trigger: containerRef.current,
          pin: true,
          start: 'top top',
          end: `+=${scrollWidth}`,
          scrub: 1.5,
          anticipatePin: 1,
        }
      });
    }, containerRef);
    return () => ctx.revert();
  }, [items]);

  return (
    <section ref={containerRef} className="h-screen w-full relative overflow-hidden bg-[#0A0A0F]" id="portfolio">
      <div className="absolute top-12 left-8 md:top-20 md:left-16 z-20 pointer-events-none">
        <p className="font-sans text-accent uppercase tracking-[0.3em] font-bold text-xs md:text-sm mb-3">Portfólio selecionado</p>
        <h2 className="font-drama italic text-5xl md:text-[5.5rem] leading-none text-ivory">Obras de Arte.</h2>
      </div>
      
      <div className="h-full flex items-center pl-8 md:pl-16 pt-16" ref={scrollRef}>
        <div className="flex gap-8 md:gap-10 pr-[30vw]" style={{ paddingLeft: '0' }}>
          {items.map((item, idx) => (
            <div key={idx} className="relative group overflow-hidden rounded-[2rem] md:rounded-[3rem] w-[80vw] md:w-[55vw] h-[55vh] md:h-[65vh] flex-shrink-0 border border-ivory/5 shadow-2xl cursor-pointer">
              {/* Névoa Cinematográfica escura que some no hover */}
              <div className="absolute inset-0 bg-primary/40 group-hover:bg-transparent transition-colors duration-1000 z-10 pointer-events-none" />
              
              {item.type === 'video' ? (
                <video 
                  src={item.url} 
                  className="w-full h-full object-cover scale-110 group-hover:scale-100 transition-transform duration-[2s] ease-[cubic-bezier(0.25,1,0.5,1)]"
                  autoPlay loop muted playsInline
                />
              ) : (
                <img 
                  src={item.url} 
                  alt={item.name}
                  loading="lazy"
                  className="w-full h-full object-cover scale-110 group-hover:scale-100 transition-transform duration-[2s] ease-[cubic-bezier(0.25,1,0.5,1)]" 
                />
              )}
              
              <div className="absolute bottom-8 left-8 z-20 overflow-hidden">
                 <p className="font-sans font-bold text-sm text-ivory tracking-widest bg-primary/80 backdrop-blur-md px-6 py-3 rounded-full border border-ivory/10 translate-y-full opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-700 ease-out shadow-xl">
                    {item.name}
                 </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

// --- App Principal ---
function App() {
  const [isModalOpen, setModalOpen] = useState(false);
  const heroTextRef = useRef(null);
  const philosophyRef = useRef(null);

  useEffect(() => {
    // Hero Animations
    const ctx = gsap.context(() => {
      gsap.from('.hero-element', {
        y: 40,
        opacity: 0,
        duration: 1,
        stagger: 0.15,
        ease: 'power3.out',
        delay: 0.2
      });
      
      // Protocol Sticky Stacking Animation
      const cards = gsap.utils.toArray('.prot-card');
      cards.forEach((card, i) => {
        if (i < cards.length - 1) {
          ScrollTrigger.create({
            trigger: cards[i + 1],
            start: 'top bottom-=10%',
            end: 'top top+=80',
            scrub: true,
            animation: gsap.to(card, {
              scale: 0.92,
              opacity: 0.4,
              filter: 'blur(10px)',
              ease: 'none'
            })
          });
        }
      });
    });

    return () => ctx.revert();
  }, []);

  return (
    <div className="w-full relative bg-background">
      {/* SVG Noise Overlay */}
      <svg className="noise-overlay" xmlns="http://www.w3.org/2000/svg">
        <filter id="noise">
          <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch" />
        </filter>
        <rect width="100%" height="100%" filter="url(#noise)" />
      </svg>

      <Navbar onOpenModal={() => setModalOpen(true)} />
      <OrcamentoModal isOpen={isModalOpen} onClose={() => setModalOpen(false)} />

      {/* --- HERO SECTION --- */}
      <section className="relative h-[100dvh] w-full flex items-end pb-16 md:pb-24 px-5 md:px-8 overflow-hidden bg-background">
        <div className="absolute inset-0 z-0">
          <div className="absolute inset-0 bg-gradient-to-t from-primary via-primary/60 to-transparent z-10" />
          <img 
            src="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=2070&auto=format&fit=crop" 
            className="w-full h-full object-cover object-bottom"
            alt="Arquitetura de luxo" 
          />
        </div>
        
        <div className="relative z-20 max-w-7xl mx-auto w-full" ref={heroTextRef}>
          <div className="max-w-4xl pt-[20vh]">
            <h1 className="flex flex-col gap-1 md:gap-2">
              <span className="hero-element font-sans font-bold text-[1.6rem] md:text-5xl lg:text-[4rem] tracking-tight leading-tight hover:text-accent transition-colors">
                Imóveis de alto padrão exigem uma apresentação
              </span>
              <span className="hero-element font-drama italic text-[2.8rem] md:text-7xl lg:text-[6.5rem] leading-[0.9] text-accent font-light">
                Cinematográfica.
              </span>
            </h1>
            <p className="hero-element font-sans text-base md:text-xl text-ivory/70 mt-6 md:mt-8 max-w-2xl font-light">
               Transformamos projetos arquitetônicos impecáveis em experiências visuais viscerais. Ajudamos arquitetos e construtoras a vender a visão perfeita antes do primeiro bloco.
            </p>
            
            <div className="hero-element mt-8 md:mt-10">
              <MagneticButton onClick={() => setModalOpen(true)} className="bg-accent text-primary px-6 md:px-8 py-3 md:py-4 rounded-[3rem] text-sm md:text-lg">
                Solicitar Orçamento <ArrowRight className="ml-2 w-4 h-4 md:w-5 md:h-5" />
              </MagneticButton>
            </div>
          </div>
        </div>
      </section>

      {/* --- FEATURES SECTION --- */}
      <section id="features" className="py-16 md:py-24 px-5 md:px-8 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-auto lg:h-[400px]">
          <DiagnosticShuffler />
          <TelemetryTypewriter />
          <CursorProtocolScheduler />
        </div>
      </section>

      {/* --- PORTFOLIO SECTION --- */}
      <CinematicPortfolio />

      {/* --- PHILOSOPHY SECTION --- */}
      <section className="relative py-20 md:py-32 px-5 md:px-8 overflow-hidden" ref={philosophyRef}>
        <div className="absolute inset-0 z-0 opacity-10">
          <img src="https://images.unsplash.com/photo-1600607688969-a5bfcd64bd15?q=80&w=2070&auto=format&fit=crop" className="w-full h-full object-cover grayscale" alt="Esculturas" />
        </div>
        <div className="relative z-10 max-w-5xl mx-auto text-center flex flex-col items-center">
          <p className="font-sans text-ivory/50 uppercase tracking-[0.2em] font-medium text-xs mb-6 md:mb-8">O Nosso Manifesto</p>
          <p className="font-sans text-lg md:text-2xl text-ivory/40 max-w-3xl mb-4 font-light">
            A maioria dos estúdios foca em entregar "imagens limpas e bonitinhas".
          </p>
          <h2 className="font-drama italic text-3xl md:text-6xl lg:text-7xl leading-tight">
            Nós focamos na engenharia da <br/>
            <span className="text-accent underline decoration-1 text-4xl md:text-8xl">conversão imobiliária.</span>
          </h2>
        </div>
      </section>

      {/* --- PROTOCOL SECTION --- */}
      <section id="protocol" className="py-16 md:py-24 max-w-7xl mx-auto px-5 md:px-8">
        <div className="mb-10 md:mb-16">
          <h2 className="font-sans font-bold text-2xl md:text-5xl tracking-tight mb-4">Arquitetura de Execução</h2>
          <p className="font-mono text-xs md:text-sm text-ivory/50">O Método Conrado 3D para criar visuais irrecusáveis.</p>
        </div>
        <div className="flex flex-col items-center w-full relative">
          
          <div className="w-full prot-card bg-slate p-6 md:p-16 rounded-[2rem] md:rounded-[3rem] sticky top-24 md:top-32 origin-top border border-slate/30 shadow-2xl flex flex-col md:flex-row gap-6 md:gap-12 items-start md:items-center min-h-[320px] md:min-h-[400px] mb-[30vh] md:mb-[40vh]">
             <div className="md:w-1/2">
                <div className="font-mono text-xs text-accent mb-4 md:mb-6 bg-accent/10 inline-block px-3 py-1 rounded-full border border-accent/20">PASSO 01</div>
                <h3 className="font-drama text-3xl md:text-5xl italic mb-4 md:mb-6">Briefing Hollywoodiano</h3>
                <p className="font-sans text-ivory/60 text-sm md:text-lg">Não recebemos apenas a planta. Nós absorvemos a alma do seu projeto: qual é a história? Qual é a dor do seu comprador? Iluminamos o projeto para a narrativa correta.</p>
             </div>
             <div className="hidden md:flex md:w-1/2 justify-center text-accent/20">
                <Building2 className="w-32 h-32 md:w-48 md:h-48" strokeWidth={0.5} />
             </div>
          </div>
          
          <div className="w-full prot-card bg-[#1E1E26] p-6 md:p-16 rounded-[2rem] md:rounded-[3rem] sticky top-28 md:top-40 origin-top border border-slate/30 shadow-2xl flex flex-col md:flex-row gap-6 md:gap-12 items-start md:items-center min-h-[320px] md:min-h-[400px] mb-[30vh] md:mb-[40vh]">
             <div className="md:w-1/2">
                <div className="font-mono text-xs text-accent mb-4 md:mb-6 bg-accent/10 inline-block px-3 py-1 rounded-full border border-accent/20">PASSO 02</div>
                <h3 className="font-drama text-3xl md:text-5xl italic mb-4 md:mb-6">Texturização Tátil</h3>
                <p className="font-sans text-ivory/60 text-sm md:text-lg">Acabamentos que o cliente quase consegue tocar pela tela. Mármores polidos com reflexos imperfeitos, couro orgânico e iluminação volumétrica.</p>
             </div>
             <div className="hidden md:flex md:w-1/2 justify-center text-accent/30">
                <Eye className="w-32 h-32 md:w-48 md:h-48" strokeWidth={0.5} />
             </div>
          </div>
          
          <div className="w-full prot-card bg-[#111116] p-6 md:p-16 rounded-[2rem] md:rounded-[3rem] sticky top-32 md:top-48 origin-top border border-accent/40 shadow-2xl flex flex-col md:flex-row gap-6 md:gap-12 items-start md:items-center min-h-[320px] md:min-h-[400px]">
             <div className="md:w-1/2">
                <div className="font-mono text-xs text-primary mb-4 md:mb-6 bg-accent inline-block px-3 py-1 rounded-full font-bold">ENTREGA FINAL</div>
                <h3 className="font-drama text-3xl md:text-5xl italic text-accent mb-4 md:mb-6">Fechamento Acelerado</h3>
                <p className="font-sans text-ivory/60 text-sm md:text-lg">O arquivo final exportado nas mais altas resoluções (4K/8K), pronto para ir para as suas campanhas de tráfego, stands de venda e anúncios premium.</p>
             </div>
             <div className="hidden md:flex md:w-1/2 justify-center text-accent">
                <LineChart className="w-32 h-32 md:w-48 md:h-48 drop-shadow-lg" strokeWidth={0.5} />
             </div>
          </div>
          
        </div>
      </section>

      {/* --- LARGE CTA --- */}
      <section className="py-20 md:py-32 px-5 md:px-8 flex justify-center">
        <div className="bg-accent/5 max-w-5xl w-full rounded-[2rem] md:rounded-[4rem] border border-accent/10 p-8 md:p-24 text-center">
          <h2 className="font-drama italic text-4xl md:text-7xl mb-6 md:mb-8">Vamos encantar?</h2>
          <p className="font-sans text-base md:text-xl text-ivory/70 max-w-2xl mx-auto mb-8 md:mb-10">O próximo investidor a ver as suas renderizações vai comprar. Você precisa estar pronto.</p>
          <MagneticButton onClick={() => setModalOpen(true)} className="bg-accent text-primary px-6 md:px-10 py-4 md:py-5 rounded-[3rem] text-base md:text-xl">
            Iniciar Projeto 3D <MessageCircle className="ml-2 md:ml-3 w-5 h-5 md:w-6 md:h-6" />
          </MagneticButton>
        </div>
      </section>

      {/* --- FOOTER --- */}
      <footer className="bg-[#05050A] pt-14 md:pt-20 pb-8 md:pb-10 px-5 md:px-8 rounded-t-[2rem] md:rounded-t-[4rem]">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-10 md:gap-12 border-b border-ivory/10 pb-12 md:pb-16">
          <div>
            <img src={logoImg} alt="Conrado 3D Studio" className="h-10 md:h-14 w-auto object-contain mb-4 md:mb-6 drop-shadow-lg opacity-90 hover:opacity-100 transition-all pointer-events-none" />
            <p className="font-sans text-ivory/40 max-w-xs text-xs md:text-sm">Estúdio especializado em apresentações arquitetônicas fotorrealistas focadas em aceleração de vendas imobiliárias.</p>
            
            <div className="mt-6 md:mt-8 flex items-center gap-3 bg-primary/50 w-max px-4 py-2 rounded-full border border-ivory/5">
              <div className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse border border-background"></div>
              <span className="font-mono text-[10px] md:text-xs text-ivory/60">SISTEMA OPERACIONAL</span>
            </div>
          </div>
          <div className="flex gap-10 md:gap-16 justify-start md:justify-end font-sans text-sm text-ivory/60">
            <div className="flex flex-col gap-3 md:gap-4">
              <p className="text-ivory font-bold font-mono text-xs mb-1 md:mb-2 tracking-widest">NAVEGAÇÃO</p>
              <a href="#features" className="hover:text-accent transition-colors">Vantagens</a>
              <a href="#portfolio" className="hover:text-accent transition-colors">Portfólio</a>
              <a href="#protocol" className="hover:text-accent transition-colors">Método</a>
              <span className="cursor-pointer hover:text-accent transition-colors" onClick={() => setModalOpen(true)}>Orçamento</span>
            </div>
            <div className="flex flex-col gap-3 md:gap-4">
              <p className="text-ivory font-bold font-mono text-xs mb-1 md:mb-2 tracking-widest">LEGAL</p>
              <a href="#" className="hover:text-ivory transition-colors">Termos de Serviço</a>
              <a href="#" className="hover:text-ivory transition-colors">Privacidade</a>
            </div>
          </div>
        </div>
        <div className="max-w-7xl mx-auto text-center font-mono text-[10px] md:text-xs text-ivory/30 mt-8 md:mt-10">
          © 2026 CONRADO 3D STUDIO. ALL RIGHTS RESERVED. PIXEL PERFECT ENGINEERING.
        </div>
      </footer>
    </div>
  );
}

export default App;
