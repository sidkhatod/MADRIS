import { useState, useRef } from "react";
import {
  Upload,
  FileText,
  MapPin,
  Image,
  Activity,
  Check,
  X,
  ChevronRight,
  Layers,
  Clock,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { api, IngestResponse } from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";

const uploadedItems = [
  { name: "SITREP_Jan21_v2.pdf", type: "Textual", status: "ready" },
  { name: "fault_lines_region.geojson", type: "Geospatial", status: "ready" },
  { name: "satellite_pre_event.jpg", type: "Visual", status: "processing" },
  { name: "seismograph_data.csv", type: "Sensor", status: "ready" },
  { name: "population_density.shp", type: "Geospatial", status: "ready" },
];

const detectedTypes = [
  { type: "Situation Reports", count: 2 },
  { type: "Geospatial Layers", count: 3 },
  { type: "Satellite Imagery", count: 1 },
  { type: "Sensor Readings", count: 1 },
];

export default function InputConsole() {
  const [activeTab, setActiveTab] = useState("textual");
  const [loading, setLoading] = useState(false);
  const [inputText, setInputText] = useState("");
  const { toast } = useToast();

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleProcess = async () => {
    if (!inputText.trim()) {
      toast({
        title: "Input Required",
        description: "Please enter text to process.",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      const caseId = `case_${Date.now()}`; // Generate a temp case ID
      const response = await api.post<IngestResponse>("/ingest/case-study", {
        case_study_id: caseId,
        raw_text: inputText,
        source_id: "manual_console",
      });

      if (response.data.status === "success") {
        toast({
          title: "Processing Complete",
          description: `Successfully created ${response.data.snapshots_created} decision snapshots.`,
        });
        setInputText("");
      }
    } catch (error) {
      console.error("Ingest failed:", error);
      toast({
        title: "Processing Failed",
        description: "Failed to ingest case study. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // 1. Size Validation (Limit to 2MB to prevent browser freeze)
      if (file.size > 2 * 1024 * 1024) {
        toast({
          title: "File Too Large",
          description: "Please upload text files smaller than 2MB to avoid freezing.",
          variant: "destructive",
        });
        return;
      }

      // 2. Type Validation (Basic check)
      if (!file.name.match(/\.(txt|md|json|csv)$/i)) {
        toast({
          title: "Invalid File Type",
          description: "Please upload .txt, .md, .json, or .csv files only.",
          variant: "destructive",
        });
        return;
      }

      const reader = new FileReader();
      reader.onloadstart = () => setLoading(true); // Reuse loading state just for visual feedback
      reader.onload = (e) => {
        const text = e.target?.result as string;
        setInputText((prev) => prev + "\n\n" + text);
        setLoading(false);
        toast({
          title: "File Loaded",
          description: `Imported content from ${file.name}`,
        });
      };
      reader.onerror = () => {
        setLoading(false);
        toast({
          title: "Read Error",
          description: "Failed to read file context.",
          variant: "destructive",
        });
      };
      reader.readAsText(file);
    }
  };

  return (
    <div className="flex h-full">
      {/* Left Panel - Input Tabs */}
      <div className="flex-1 border-r border-border overflow-auto">
        <div className="p-6">
          <div className="mb-6">
            <h1 className="text-xl font-semibold text-foreground">Input Console</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Ingest multi-modal disaster data for analysis
            </p>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="w-full grid grid-cols-4 h-auto p-1 bg-secondary">
              <TabsTrigger
                value="textual"
                className="flex flex-col gap-1 py-3 data-[state=active]:bg-background"
              >
                <FileText className="h-4 w-4" />
                <span className="text-xs">Textual</span>
              </TabsTrigger>
              <TabsTrigger
                value="geospatial"
                className="flex flex-col gap-1 py-3 data-[state=active]:bg-background"
              >
                <MapPin className="h-4 w-4" />
                <span className="text-xs">Geospatial</span>
              </TabsTrigger>
              <TabsTrigger
                value="visual"
                className="flex flex-col gap-1 py-3 data-[state=active]:bg-background"
              >
                <Image className="h-4 w-4" />
                <span className="text-xs">Visual</span>
              </TabsTrigger>
              <TabsTrigger
                value="sensor"
                className="flex flex-col gap-1 py-3 data-[state=active]:bg-background"
              >
                <Activity className="h-4 w-4" />
                <span className="text-xs">Sensor</span>
              </TabsTrigger>
            </TabsList>

            {/* Textual Inputs */}
            <TabsContent value="textual" className="mt-6 space-y-6">
              <div className="content-card">
                <h3 className="text-sm font-semibold text-foreground mb-4">
                  Document Upload
                </h3>
                <div
                  className="rounded-lg border-2 border-dashed border-border bg-muted/30 p-6 text-center cursor-pointer hover:bg-muted/50 transition-colors"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <input
                    type="file"
                    ref={fileInputRef}
                    className="hidden"
                    accept=".txt,.md,.json,.csv"
                    onChange={handleFileUpload}
                  />
                  <Upload className="mx-auto mb-2 h-8 w-8 text-muted-foreground" />
                  <p className="text-sm font-medium text-foreground">
                    Drop files or click to upload
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    TXT, MD, JSON up to 50MB
                  </p>
                </div>
              </div>

              <div className="content-card">
                <h3 className="text-sm font-semibold text-foreground mb-4">
                  Text Input
                </h3>
                <textarea
                  rows={8}
                  placeholder="Paste report content, field notes, or any textual data..."
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring resize-none"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                />
              </div>

              <div className="content-card">
                <h3 className="text-sm font-semibold text-foreground mb-4">
                  Report Type
                </h3>
                <Select>
                  <SelectTrigger className="w-full bg-background">
                    <SelectValue placeholder="Select report type" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover border border-border">
                    <SelectItem value="sitrep">SITREP</SelectItem>
                    <SelectItem value="government">Government Bulletin</SelectItem>
                    <SelectItem value="ngo">NGO / Field Report</SelectItem>
                    <SelectItem value="historical">Historical Case Study</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </TabsContent>

            {/* Geospatial Inputs */}
            <TabsContent value="geospatial" className="mt-6 space-y-6">
              <div className="content-card">
                <h3 className="text-sm font-semibold text-foreground mb-4">
                  Geospatial File Upload
                </h3>
                <div className="rounded-lg border-2 border-dashed border-border bg-muted/30 p-6 text-center">
                  <Upload className="mx-auto mb-2 h-8 w-8 text-muted-foreground" />
                  <p className="text-sm font-medium text-foreground">
                    Drop GIS files or click to upload
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    GeoJSON, SHP, KML, KMZ
                  </p>
                </div>
              </div>

              <div className="content-card">
                <h3 className="text-sm font-semibold text-foreground mb-4">
                  Layer Overlays
                </h3>
                <div className="space-y-4">
                  {[
                    { label: "Fault Lines", description: "Tectonic fault boundaries" },
                    { label: "Population Density", description: "Census-based density map" },
                    { label: "Hospitals", description: "Medical facility locations" },
                    { label: "Roads", description: "Transportation network" },
                  ].map((layer) => (
                    <div
                      key={layer.label}
                      className="flex items-center justify-between rounded-lg border border-border bg-background p-3"
                    >
                      <div>
                        <p className="text-sm font-medium text-foreground">
                          {layer.label}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {layer.description}
                        </p>
                      </div>
                      <Switch />
                    </div>
                  ))}
                </div>
              </div>

              <div className="content-card">
                <h3 className="text-sm font-semibold text-foreground mb-4">
                  Map Preview
                </h3>
                <div className="relative aspect-video rounded-lg bg-gradient-to-br from-slate-200 to-slate-300 overflow-hidden">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <Layers className="mx-auto mb-2 h-8 w-8 text-slate-400" />
                      <p className="text-sm font-medium text-slate-500">
                        Layer Preview
                      </p>
                      <p className="text-xs text-slate-400">
                        Enable layers above to preview
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>

            {/* Visual Inputs */}
            <TabsContent value="visual" className="mt-6 space-y-6">
              <div className="content-card">
                <h3 className="text-sm font-semibold text-foreground mb-4">
                  Image Upload
                </h3>
                <div className="grid grid-cols-3 gap-3">
                  {[1, 2, 3, 4, 5, 6].map((i) => (
                    <div
                      key={i}
                      className="aspect-square rounded-lg border-2 border-dashed border-border bg-muted/30 flex items-center justify-center cursor-pointer hover:bg-muted/50 transition-colors"
                    >
                      <Upload className="h-6 w-6 text-muted-foreground" />
                    </div>
                  ))}
                </div>
              </div>

              <div className="content-card">
                <h3 className="text-sm font-semibold text-foreground mb-4">
                  Image Timeline
                </h3>
                <div className="flex gap-2">
                  <button className="flex-1 rounded-lg border-2 border-primary bg-primary/5 p-3 text-center">
                    <p className="text-sm font-medium text-primary">Pre-Event</p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      Before disaster
                    </p>
                  </button>
                  <button className="flex-1 rounded-lg border border-border bg-background p-3 text-center hover:bg-secondary transition-colors">
                    <p className="text-sm font-medium text-foreground">Post-Event</p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      After disaster
                    </p>
                  </button>
                </div>
              </div>

              <div className="content-card">
                <h3 className="text-sm font-semibold text-foreground mb-4">
                  Image Category
                </h3>
                <Select>
                  <SelectTrigger className="w-full bg-background">
                    <SelectValue placeholder="Select image source" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover border border-border">
                    <SelectItem value="satellite">Satellite</SelectItem>
                    <SelectItem value="drone">Drone</SelectItem>
                    <SelectItem value="street">Street-level</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </TabsContent>

            {/* Sensor Inputs */}
            <TabsContent value="sensor" className="mt-6 space-y-6">
              <div className="content-card">
                <h3 className="text-sm font-semibold text-foreground mb-4">
                  Sensor Data Upload
                </h3>
                <div className="rounded-lg border-2 border-dashed border-border bg-muted/30 p-6 text-center">
                  <Upload className="mx-auto mb-2 h-8 w-8 text-muted-foreground" />
                  <p className="text-sm font-medium text-foreground">
                    Drop data files or click to upload
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    CSV, JSON, XML
                  </p>
                </div>
              </div>

              <div className="content-card">
                <h3 className="text-sm font-semibold text-foreground mb-4">
                  Data Type
                </h3>
                <Select>
                  <SelectTrigger className="w-full bg-background">
                    <SelectValue placeholder="Select data type" />
                  </SelectTrigger>
                  <SelectContent className="bg-popover border border-border">
                    <SelectItem value="seismograph">Seismograph Readings</SelectItem>
                    <SelectItem value="aftershock">Aftershock Probability</SelectItem>
                    <SelectItem value="weather">Weather Forecast</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="content-card">
                <h3 className="text-sm font-semibold text-foreground mb-4">
                  Time Range
                </h3>
                <div className="flex gap-3">
                  <div className="flex-1">
                    <label className="text-xs text-muted-foreground mb-1.5 block">
                      Start
                    </label>
                    <div className="flex items-center gap-2 rounded-md border border-input bg-background px-3 py-2">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm text-foreground">Jan 20, 00:00</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <label className="text-xs text-muted-foreground mb-1.5 block">
                      End
                    </label>
                    <div className="flex items-center gap-2 rounded-md border border-input bg-background px-3 py-2">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm text-foreground">Jan 21, 23:59</span>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {/* Right Panel - Input Summary */}
      <div className="w-80 bg-card overflow-auto">
        <div className="p-6">
          <h2 className="text-base font-semibold text-foreground mb-4">
            Input Summary
          </h2>

          {/* Uploaded Items */}
          <div className="mb-6">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
              Uploaded Items
            </h3>
            <div className="space-y-2">
              {uploadedItems.map((item, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 rounded-lg border border-border bg-background p-3"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">
                      {item.name}
                    </p>
                    <p className="text-xs text-muted-foreground">{item.type}</p>
                  </div>
                  {item.status === "ready" ? (
                    <Check className="h-4 w-4 text-emerald-500 shrink-0" />
                  ) : (
                    <div className="h-4 w-4 rounded-full border-2 border-primary border-t-transparent animate-spin shrink-0" />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Detected Types */}
          <div className="mb-6">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
              Detected Input Types
            </h3>
            <div className="space-y-2">
              {detectedTypes.map((type, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between rounded-lg bg-secondary px-3 py-2"
                >
                  <span className="text-sm text-foreground">{type.type}</span>
                  <span className="text-xs font-medium text-muted-foreground">
                    {type.count}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Data Completeness */}
          <div className="mb-6">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
              Data Completeness
            </h3>
            <div className="rounded-lg border border-border bg-background p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-foreground">Overall Score</span>
                <span className="text-sm font-semibold text-amber-600">Medium</span>
              </div>
              <div className="h-2 rounded-full bg-secondary">
                <div className="h-full w-3/5 rounded-full bg-amber-500" />
              </div>
              <div className="mt-3 space-y-1.5">
                <div className="flex items-center gap-2 text-xs">
                  <Check className="h-3 w-3 text-emerald-500" />
                  <span className="text-muted-foreground">
                    Textual reports available
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <Check className="h-3 w-3 text-emerald-500" />
                  <span className="text-muted-foreground">
                    Geospatial data loaded
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <X className="h-3 w-3 text-red-500" />
                  <span className="text-muted-foreground">
                    Missing: Post-event imagery
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Process Button */}
          <Button
            className="w-full"
            size="lg"
            onClick={handleProcess}
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                Process Inputs
                <ChevronRight className="ml-2 h-4 w-4" />
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
