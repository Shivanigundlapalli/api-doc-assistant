import { AppLayout } from "@/components/layout/app-layout"
import { Skeleton } from "@/components/ui/skeleton"

export default function Loading() {
  return (
    <AppLayout>
      <div className="flex-1 flex flex-col p-8 max-w-4xl mx-auto w-full">
        <div className="flex gap-4 py-6">
          <Skeleton className="h-8 w-8 rounded-full" />
          <div className="space-y-2 flex-1 pt-1">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </div>
        </div>
        <div className="flex gap-4 py-6">
          <Skeleton className="h-8 w-8 rounded-lg" />
          <div className="space-y-4 flex-1">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-[90%]" />
            <Skeleton className="h-4 w-4/5" />
            <div className="mt-4 pt-4 border-t">
              <Skeleton className="h-[120px] w-full rounded-md" />
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
