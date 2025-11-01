import { useState } from 'react'
import { Upload, FileText, Sparkles, Settings, Loader2 } from 'lucide-react'

import './index.css'
import { Button } from './components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs'
import { Label } from './components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select'
import { Switch } from './components/ui/switch'
import { Textarea } from './components/ui/textarea'
import { useToast } from './hooks/use-toast'
import { Toaster } from './components/ui/toaster'
import { uploadFileChunked, formatFileSize } from './lib/chunkedUpload'

interface OCRResult {
  text: string
  confidence: number
  word_count: number
  character_count: number
  language: string
}

interface GeminiResult {
  success: boolean
  response: string
  task: string
}

function App() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [ocrResult, setOcrResult] = useState<OCRResult | null>(null)
  const [geminiResult, setGeminiResult] = useState<GeminiResult | null>(null)

  // OCR Settings
  const [language, setLanguage] = useState('eng')
  const [preprocess, setPreprocess] = useState(false)
  const [useGemini, setUseGemini] = useState(false)
  const [geminiTask, setGeminiTask] = useState('analyze')
  const [customPrompt, setCustomPrompt] = useState('')

  const { toast } = useToast()

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      setFile(selectedFile)
      setOcrResult(null)
      setGeminiResult(null)
      setUploadProgress(0)
      
      // Show file size info
      const size = formatFileSize(selectedFile.size)
      const isLarge = selectedFile.size > 10 * 1024 * 1024
      
      if (isLarge) {
        toast({
          title: "Large file detected",
          description: `File size: ${size}. Will use chunked upload for faster processing.`
        })
      }
    }
  }

  const handleProcess = async () => {
    if (!file) {
      toast({
        title: "No file selected",
        description: "Please select an image file to process",
        variant: "destructive"
      })
      return
    }

    setLoading(true)
    setUploadProgress(0)

    try {
      // Use chunked upload utility (handles both small and large files)
      const result = await uploadFileChunked({
        file,
        language,
        preprocess,
        useGemini,
        geminiTask,
        geminiPrompt: customPrompt,
        onProgress: (progress) => {
          setUploadProgress(Math.round(progress))
        },
        onChunkComplete: (chunk, total) => {
          console.log(`Uploaded chunk ${chunk + 1}/${total}`)
        }
      })

      if (result.success) {
        if (useGemini && result.data.gemini) {
          setOcrResult(result.data.ocr)
          setGeminiResult(result.data.gemini)
          toast({
            title: "Success!",
            description: "Document processed with AI analysis"
          })
        } else {
          setOcrResult(result.data.ocr || result.data)
          toast({
            title: "Success!",
            description: "Text extracted from document"
          })
        }
      } else {
        throw new Error(result.error || 'Processing failed')
      }
    } catch (error: any) {
      console.error('Upload error:', error)
      toast({
        title: "Error",
        description: error.message || error.response?.data?.error || "Failed to process document",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
      setUploadProgress(0)
    }
  }

  const copyToClipboard = (text: string, type: string) => {
    navigator.clipboard.writeText(text)
    toast({
      title: "Copied!",
      description: `${type} copied to clipboard`
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto p-6 max-w-7xl">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 dark:text-white mb-2">
            OCR Gaby
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            Extract text from images with OCR and AI-powered analysis
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Upload and Settings */}
          <div className="lg:col-span-1 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="w-5 h-5" />
                  Upload Document
                </CardTitle>
                <CardDescription>
                  Select an image file to extract text
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-lg p-8 text-center hover:border-slate-400 dark:hover:border-slate-600 transition-colors">
                  <input
                    type="file"
                    id="file-upload"
                    className="hidden"
                    accept="image/*,.pdf"
                    onChange={handleFileChange}
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <FileText className="w-12 h-12 mx-auto mb-4 text-slate-400" />
                    <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">
                      {file ? (
                        <>
                          <span className="font-medium">{file.name}</span>
                          <br />
                          <span className="text-xs">{formatFileSize(file.size)}</span>
                        </>
                      ) : (
                        'Click to select file'
                      )}
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-500">
                      JPG, PNG, PDF up to 50MB
                    </p>
                  </label>
                </div>

                {/* Upload Progress Bar */}
                {loading && uploadProgress > 0 && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm text-slate-600 dark:text-slate-400">
                      <span>Uploading...</span>
                      <span>{uploadProgress}%</span>
                    </div>
                    <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      />
                    </div>
                  </div>
                )}

                <Button 
                  onClick={handleProcess} 
                  disabled={!file || loading}
                  className="w-full"
                  size="lg"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      {uploadProgress > 0 && uploadProgress < 100 
                        ? `Uploading... ${uploadProgress}%` 
                        : 'Processing...'}
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 mr-2" />
                      Process Document
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="w-5 h-5" />
                  Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="language">Language</Label>
                  <Select value={language} onValueChange={setLanguage}>
                    <SelectTrigger id="language">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="eng">English</SelectItem>
                      <SelectItem value="spa">Spanish</SelectItem>
                      <SelectItem value="fra">French</SelectItem>
                      <SelectItem value="deu">German</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex items-center justify-between">
                  <Label htmlFor="preprocess">Image Preprocessing</Label>
                  <Switch
                    id="preprocess"
                    checked={preprocess}
                    onCheckedChange={setPreprocess}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <Label htmlFor="gemini">AI Analysis (Gemini)</Label>
                  <Switch
                    id="gemini"
                    checked={useGemini}
                    onCheckedChange={setUseGemini}
                  />
                </div>

                {useGemini && (
                  <>
                    <div className="space-y-2">
                      <Label htmlFor="gemini-task">AI Task</Label>
                      <Select value={geminiTask} onValueChange={setGeminiTask}>
                        <SelectTrigger id="gemini-task">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="analyze">Analyze</SelectItem>
                          <SelectItem value="summarize">Summarize</SelectItem>
                          <SelectItem value="extract">Extract Data</SelectItem>
                          <SelectItem value="structure">Structure</SelectItem>
                          <SelectItem value="translate">Translate</SelectItem>
                          <SelectItem value="validate">Validate</SelectItem>
                          <SelectItem value="format">Format</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="custom-prompt">Custom Prompt (Optional)</Label>
                      <Textarea
                        id="custom-prompt"
                        placeholder="e.g., Extract all dates and amounts..."
                        value={customPrompt}
                        onChange={(e) => setCustomPrompt(e.target.value)}
                        rows={3}
                      />
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Results */}
          <div className="lg:col-span-2">
            <Card className="h-full">
              <CardHeader>
                <CardTitle>Results</CardTitle>
                <CardDescription>
                  Extracted text and AI analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                {!ocrResult && !geminiResult && (
                  <div className="flex flex-col items-center justify-center h-96 text-center">
                    <FileText className="w-16 h-16 text-slate-300 dark:text-slate-700 mb-4" />
                    <p className="text-slate-500 dark:text-slate-400">
                      No results yet. Upload and process a document to get started.
                    </p>
                  </div>
                )}

                {(ocrResult || geminiResult) && (
                  <Tabs defaultValue="ocr" className="w-full">
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger value="ocr">OCR Text</TabsTrigger>
                      <TabsTrigger value="gemini" disabled={!geminiResult}>
                        AI Analysis
                      </TabsTrigger>
                    </TabsList>

                    <TabsContent value="ocr" className="space-y-4">
                      {ocrResult && (
                        <>
                          <div className="grid grid-cols-4 gap-4">
                            <div className="bg-slate-100 dark:bg-slate-800 p-4 rounded-lg">
                              <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Confidence</p>
                              <p className="text-2xl font-bold text-slate-900 dark:text-white">
                                {ocrResult.confidence}%
                              </p>
                            </div>
                            <div className="bg-slate-100 dark:bg-slate-800 p-4 rounded-lg">
                              <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Words</p>
                              <p className="text-2xl font-bold text-slate-900 dark:text-white">
                                {ocrResult.word_count}
                              </p>
                            </div>
                            <div className="bg-slate-100 dark:bg-slate-800 p-4 rounded-lg">
                              <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Characters</p>
                              <p className="text-2xl font-bold text-slate-900 dark:text-white">
                                {ocrResult.character_count}
                              </p>
                            </div>
                            <div className="bg-slate-100 dark:bg-slate-800 p-4 rounded-lg">
                              <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Language</p>
                              <p className="text-2xl font-bold text-slate-900 dark:text-white uppercase">
                                {ocrResult.language}
                              </p>
                            </div>
                          </div>

                          <div className="bg-slate-50 dark:bg-slate-900 p-6 rounded-lg border border-slate-200 dark:border-slate-700">
                            <pre className="whitespace-pre-wrap font-mono text-sm text-slate-700 dark:text-slate-300">
                              {ocrResult.text}
                            </pre>
                          </div>

                          <Button 
                            variant="outline" 
                            className="w-full"
                            onClick={() => copyToClipboard(ocrResult.text, 'OCR text')}
                          >
                            Copy to Clipboard
                          </Button>
                        </>
                      )}
                    </TabsContent>

                    <TabsContent value="gemini" className="space-y-4">
                      {geminiResult && geminiResult.success && (
                        <>
                          <div className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 p-4 rounded-lg border border-purple-200 dark:border-purple-800">
                            <div className="flex items-center gap-2 mb-2">
                              <Sparkles className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                              <p className="font-semibold text-purple-900 dark:text-purple-100">
                                AI Analysis - {geminiResult.task}
                              </p>
                            </div>
                          </div>

                          <div className="bg-slate-50 dark:bg-slate-900 p-6 rounded-lg border border-slate-200 dark:border-slate-700">
                            <div className="prose dark:prose-invert max-w-none">
                              <pre className="whitespace-pre-wrap font-sans text-sm text-slate-700 dark:text-slate-300">
                                {geminiResult.response}
                              </pre>
                            </div>
                          </div>

                          <Button 
                            variant="outline" 
                            className="w-full"
                            onClick={() => copyToClipboard(geminiResult.response, 'AI analysis')}
                          >
                            Copy Analysis
                          </Button>
                        </>
                      )}
                    </TabsContent>
                  </Tabs>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
      <Toaster />
    </div>
  )
}

export default App
