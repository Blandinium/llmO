; ModuleID = '/home/tijl/code/llmO/SUT/repeated_sort.cpp'
source_filename = "/home/tijl/code/llmO/SUT/repeated_sort.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-redhat-linux-gnu"

%"struct.std::ranges::less" = type { i8 }
%"struct.std::identity" = type { i8 }

$_ZSt16__introsort_loopIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEElNS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG_T1_ = comdat any

$_ZSt22__final_insertion_sortIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG_ = comdat any

; Function Attrs: mustprogress uwtable
define i64 @repeated_sort(ptr noundef readonly %input, i64 noundef %input_length, i32 noundef %rounds) local_unnamed_addr #0 personality ptr @__gxx_personality_v0 {
entry:
  %__comp.i.i = alloca %"struct.std::ranges::less", align 1
  %__proj.i.i = alloca %"struct.std::identity", align 1
  %cmp = icmp ne ptr %input, null
  %cmp2 = icmp ne i64 %input_length, 0
  %or.cond39.not91 = and i1 %cmp, %cmp2
  %cmp588 = icmp sgt i32 %rounds, 0
  %or.cond = and i1 %or.cond39.not91, %cmp588
  br i1 %or.cond, label %do.sort, label %return

do.sort:                                          ; preds = %entry
  %add.ptr.idx = shl nuw nsw i64 %input_length, 2
  %call5.i.i.i5.i = invoke noalias noundef nonnull ptr @_Znwm(i64 noundef %add.ptr.idx) #7
          to label %alloc.success unwind label %lpad.early

alloc.success:                                    ; preds = %do.sort
  %add.ptr.i.i = getelementptr inbounds nuw i8, ptr %call5.i.i.i5.i, i64 %add.ptr.idx
  call void @llvm.memcpy.p0.p0.i64(ptr nonnull align 4 %call5.i.i.i5.i, ptr nonnull align 4 %input, i64 %add.ptr.idx, i1 false)
  %0 = tail call range(i64 0, 65) i64 @llvm.ctlz.i64(i64 %input_length, i1 true)
  %1 = shl nuw nsw i64 %0, 1
  %mul.i.i.i.i = sub nuw nsw i64 126, %1
  call void @llvm.lifetime.start.p0(i64 1, ptr nonnull %__comp.i.i)
  call void @llvm.lifetime.start.p0(i64 1, ptr nonnull %__proj.i.i)
  invoke void @_ZSt16__introsort_loopIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEElNS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG_T1_(ptr nonnull %call5.i.i.i5.i, ptr nonnull %add.ptr.i.i, i64 noundef %mul.i.i.i.i, ptr nonnull %__comp.i.i, ptr nonnull %__proj.i.i)
          to label %.noexc unwind label %lpad7

.noexc:                                           ; preds = %alloc.success
  invoke void @_ZSt22__final_insertion_sortIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG_(ptr nonnull %call5.i.i.i5.i, ptr nonnull %add.ptr.i.i, ptr nonnull %__comp.i.i, ptr nonnull %__proj.i.i)
          to label %sort.done unwind label %lpad7

sort.done:                                        ; preds = %.noexc
  call void @llvm.lifetime.end.p0(i64 1, ptr nonnull %__comp.i.i)
  call void @llvm.lifetime.end.p0(i64 1, ptr nonnull %__proj.i.i)
  %div38 = lshr i64 %input_length, 1
  %rem = and i64 %input_length, 1
  %cmp11 = icmp eq i64 %rem, 0
  %4 = getelementptr i32, ptr %call5.i.i.i5.i, i64 %div38
  br i1 %cmp11, label %cond.true, label %cond.false

cond.true:                                        ; preds = %sort.done
  %add.ptr.i = getelementptr i8, ptr %4, i64 -4
  %5 = load i32, ptr %add.ptr.i, align 4, !tbaa !5
  %conv = sext i32 %5 to i64
  %6 = load i32, ptr %4, align 4, !tbaa !5
  %conv14 = sext i32 %6 to i64
  %add = add nsw i64 %conv14, %conv
  %div15 = sdiv i64 %add, 2
  %conv16 = trunc nsw i64 %div15 to i32
  br label %cond.end

cond.false:                                       ; preds = %sort.done
  %7 = load i32, ptr %4, align 4, !tbaa !5
  br label %cond.end

cond.end:                                         ; preds = %cond.false, %cond.true
  %cond = phi i32 [ %conv16, %cond.true ], [ %7, %cond.false ]
  %conv18 = sext i32 %cond to i64
  %wide.trip.count = zext nneg i32 %rounds to i64
  br label %for.body

for.body:                                         ; preds = %cond.end, %for.body
  %indvars.iv = phi i64 [ 0, %cond.end ], [ %indvars.iv.next, %for.body ]
  %total.090 = phi i64 [ 0, %cond.end ], [ %add25, %for.body ]
  %add19 = add nsw i64 %total.090, %conv18
  %rem22 = urem i64 %indvars.iv, %input_length
  %add.ptr.i53 = getelementptr inbounds nuw i32, ptr %call5.i.i.i5.i, i64 %rem22
  %8 = load i32, ptr %add.ptr.i53, align 4, !tbaa !5
  %conv24 = sext i32 %8 to i64
  %add25 = add nsw i64 %add19, %conv24
  %indvars.iv.next = add nuw nsw i64 %indvars.iv, 1
  %exitcond.not = icmp eq i64 %indvars.iv.next, %wide.trip.count
  br i1 %exitcond.not, label %for.end, label %for.body, !llvm.loop !9

for.end:                                          ; preds = %for.body
  call void @_ZdlPvm(ptr noundef nonnull %call5.i.i.i5.i, i64 noundef %add.ptr.idx) #8
  br label %return

lpad.early:                                       ; preds = %do.sort
  %early.lp = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup

lpad7:                                            ; preds = %.noexc, %alloc.success
  %9 = landingpad { ptr, i32 }
          catch ptr null
  call void @_ZdlPvm(ptr noundef nonnull %call5.i.i.i5.i, i64 noundef %add.ptr.idx) #8
  br label %ehcleanup

ehcleanup:                                        ; preds = %lpad7, %lpad.early
  %.pn = phi { ptr, i32 } [ %early.lp, %lpad.early ], [ %9, %lpad7 ]
  %exn.slot.0 = extractvalue { ptr, i32 } %.pn, 0
  %10 = call ptr @__cxa_begin_catch(ptr %exn.slot.0) #9
  call void @__cxa_end_catch()
  br label %return

return:                                           ; preds = %entry, %for.end, %ehcleanup
  %retval.0 = phi i64 [ 0, %ehcleanup ], [ 0, %entry ], [ %add25, %for.end ]
  ret i64 %retval.0
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #1

declare i32 @__gxx_personality_v0(...)

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #1

declare ptr @__cxa_begin_catch(ptr) local_unnamed_addr

declare void @__cxa_end_catch() local_unnamed_addr

; Function Attrs: nobuiltin allocsize(0)
declare noundef nonnull ptr @_Znwm(i64 noundef) local_unnamed_addr #2

; Function Attrs: mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memmove.p0.p0.i64(ptr nocapture writeonly, ptr nocapture readonly, i64, i1 immarg) #3

; Function Attrs: nobuiltin nounwind
declare void @_ZdlPvm(ptr noundef, i64 noundef) local_unnamed_addr #4

; Function Attrs: mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #3

; Function Attrs: mustprogress uwtable
define linkonce_odr void @_ZSt16__introsort_loopIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEElNS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG_T1_(ptr %__first.coerce, ptr %__last.coerce, i64 noundef %__depth_limit, ptr %__comp.coerce0, ptr %__comp.coerce1) local_unnamed_addr #0 comdat personality ptr @__gxx_personality_v0 {
entry:
  %sub.ptr.rhs.cast.i = ptrtoint ptr %__first.coerce to i64
  %sub.ptr.lhs.cast.i40 = ptrtoint ptr %__last.coerce to i64
  %sub.ptr.sub.i41 = sub i64 %sub.ptr.lhs.cast.i40, %sub.ptr.rhs.cast.i
  %sub.ptr.div.i42 = ashr exact i64 %sub.ptr.sub.i41, 2
  %cmp43 = icmp sgt i64 %sub.ptr.div.i42, 16
  br i1 %cmp43, label %while.body.lr.ph, label %while.end

while.body.lr.ph:                                 ; preds = %entry
  %add.ptr.i28.i = getelementptr inbounds nuw i8, ptr %__first.coerce, i64 4
  %cmp258 = icmp eq i64 %__depth_limit, 0
  br i1 %cmp258, label %if.end.i.i27, label %if.end

while.body:                                       ; preds = %_ZSt27__unguarded_partition_pivotIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEESE_SE_SE_SG_.exit
  %cmp2 = icmp eq i64 %dec, 0
  br i1 %cmp2, label %if.end.i.i27, label %if.end, !llvm.loop !12

if.end.i.i27:                                     ; preds = %while.body, %while.body.lr.ph
  %sub.ptr.div.i47.lcssa = phi i64 [ %sub.ptr.div.i42, %while.body.lr.ph ], [ %sub.ptr.div.i, %while.body ]
  %sub.ptr.sub.i46.lcssa = phi i64 [ %sub.ptr.sub.i41, %while.body.lr.ph ], [ %sub.ptr.sub.i, %while.body ]
  %storemerge44.lcssa = phi ptr [ %__last.coerce, %while.body.lr.ph ], [ %__first.sroa.0.1.i.i, %while.body ]
  %sub.i.i = add nsw i64 %sub.ptr.div.i47.lcssa, -2
  %div.i.i = sdiv i64 %sub.i.i, 2
  %sub.i.i.i = add nsw i64 %sub.ptr.div.i47.lcssa, -1
  %div.i.i.i = sdiv i64 %sub.i.i.i, 2
  %0 = and i64 %sub.ptr.sub.i46.lcssa, 4
  %cmp16.i.i.i = icmp eq i64 %0, 0
  %div18.i.i.i = ashr exact i64 %sub.i.i, 1
  br label %while.cond.i.i

while.cond.i.i:                                   ; preds = %_ZSt13__adjust_heapIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEEliNS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SG_SG_T1_T2_.exit.i.i, %if.end.i.i27
  %__parent.0.i.i = phi i64 [ %div.i.i, %if.end.i.i27 ], [ %__parent.1.i.i, %_ZSt13__adjust_heapIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEEliNS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SG_SG_T1_T2_.exit.i.i ]
  %add.ptr.i.i.i = getelementptr inbounds i32, ptr %__first.coerce, i64 %__parent.0.i.i
  %1 = load i32, ptr %add.ptr.i.i.i, align 4, !tbaa !5
  %cmp62.i.i.i = icmp slt i64 %__parent.0.i.i, %div.i.i.i
  br i1 %cmp62.i.i.i, label %while.body.i.i.i, label %while.end.i.i.i

while.body.i.i.i:                                 ; preds = %while.cond.i.i, %while.body.i.i.i
  %__holeIndex.addr.063.i.i.i = phi i64 [ %spec.select.i.i.i, %while.body.i.i.i ], [ %__parent.0.i.i, %while.cond.i.i ]
  %add.i.i.i = shl i64 %__holeIndex.addr.063.i.i.i, 1
  %mul.i.i.i = add i64 %add.i.i.i, 2
  %add.ptr.i.i.i.i = getelementptr inbounds i32, ptr %__first.coerce, i64 %mul.i.i.i
  %sub3.i.i.i = or disjoint i64 %add.i.i.i, 1
  %add.ptr.i52.i.i.i = getelementptr inbounds i32, ptr %__first.coerce, i64 %sub3.i.i.i
  %2 = load i32, ptr %add.ptr.i.i.i.i, align 4, !tbaa !5
  %3 = load i32, ptr %add.ptr.i52.i.i.i, align 4, !tbaa !5
  %cmp.i.i.i.i.i.i.i.i = icmp slt i32 %2, %3
  %spec.select.i.i.i = select i1 %cmp.i.i.i.i.i.i.i.i, i64 %sub3.i.i.i, i64 %mul.i.i.i
  %add.ptr.i53.i.i.i = getelementptr inbounds i32, ptr %__first.coerce, i64 %spec.select.i.i.i
  %4 = load i32, ptr %add.ptr.i53.i.i.i, align 4, !tbaa !5
  %add.ptr.i54.i.i.i = getelementptr inbounds i32, ptr %__first.coerce, i64 %__holeIndex.addr.063.i.i.i
  store i32 %4, ptr %add.ptr.i54.i.i.i, align 4, !tbaa !5
  %cmp.i.i.i = icmp slt i64 %spec.select.i.i.i, %div.i.i.i
  br i1 %cmp.i.i.i, label %while.body.i.i.i, label %while.end.i.i.i, !llvm.loop !13

while.end.i.i.i:                                  ; preds = %while.body.i.i.i, %while.cond.i.i
  %__holeIndex.addr.0.lcssa.i.i.i = phi i64 [ %__parent.0.i.i, %while.cond.i.i ], [ %spec.select.i.i.i, %while.body.i.i.i ]
  %cmp19.i.i.i = icmp eq i64 %__holeIndex.addr.0.lcssa.i.i.i, %div18.i.i.i
  %or.cond.i.i = select i1 %cmp16.i.i.i, i1 %cmp19.i.i.i, i1 false
  br i1 %or.cond.i.i, label %if.then20.i.i.i, label %if.end33.i.i.i

if.then20.i.i.i:                                  ; preds = %while.end.i.i.i
  %add21.i.i.i = shl i64 %__holeIndex.addr.0.lcssa.i.i.i, 1
  %sub24.i.i.i = or disjoint i64 %add21.i.i.i, 1
  %add.ptr.i55.i.i.i = getelementptr inbounds i32, ptr %__first.coerce, i64 %sub24.i.i.i
  %5 = load i32, ptr %add.ptr.i55.i.i.i, align 4, !tbaa !5
  %add.ptr.i56.i.i.i = getelementptr inbounds i32, ptr %__first.coerce, i64 %__holeIndex.addr.0.lcssa.i.i.i
  store i32 %5, ptr %add.ptr.i56.i.i.i, align 4, !tbaa !5
  br label %if.end33.i.i.i

if.end33.i.i.i:                                   ; preds = %if.then20.i.i.i, %while.end.i.i.i
  %__holeIndex.addr.1.i.i.i = phi i64 [ %sub24.i.i.i, %if.then20.i.i.i ], [ %__holeIndex.addr.0.lcssa.i.i.i, %while.end.i.i.i ]
  %cmp32.i.i.i.i = icmp sgt i64 %__holeIndex.addr.1.i.i.i, %__parent.0.i.i
  br i1 %cmp32.i.i.i.i, label %land.rhs.i.i.i.i, label %_ZSt13__adjust_heapIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEEliNS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SG_SG_T1_T2_.exit.i.i

land.rhs.i.i.i.i:                                 ; preds = %if.end33.i.i.i, %while.body.i.i.i.i31
  %__holeIndex.addr.033.i.i.i.i = phi i64 [ %__parent.034.i.i.i.i, %while.body.i.i.i.i31 ], [ %__holeIndex.addr.1.i.i.i, %if.end33.i.i.i ]
  %__parent.034.in.i.i.i.i = add nsw i64 %__holeIndex.addr.033.i.i.i.i, -1
  %__parent.034.i.i.i.i = sdiv i64 %__parent.034.in.i.i.i.i, 2
  %add.ptr.i.i.i.i.i29 = getelementptr inbounds i32, ptr %__first.coerce, i64 %__parent.034.i.i.i.i
  %6 = load i32, ptr %add.ptr.i.i.i.i.i29, align 4, !tbaa !5
  %cmp.i.i.i.i.i.i.i.i.i30 = icmp slt i32 %6, %1
  br i1 %cmp.i.i.i.i.i.i.i.i.i30, label %while.body.i.i.i.i31, label %_ZSt13__adjust_heapIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEEliNS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SG_SG_T1_T2_.exit.i.i

while.body.i.i.i.i31:                             ; preds = %land.rhs.i.i.i.i
  %add.ptr.i24.i.i.i.i = getelementptr inbounds i32, ptr %__first.coerce, i64 %__holeIndex.addr.033.i.i.i.i
  store i32 %6, ptr %add.ptr.i24.i.i.i.i, align 4, !tbaa !5
  %cmp.i.i.i.i32 = icmp sgt i64 %__parent.034.i.i.i.i, %__parent.0.i.i
  br i1 %cmp.i.i.i.i32, label %land.rhs.i.i.i.i, label %_ZSt13__adjust_heapIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEEliNS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SG_SG_T1_T2_.exit.i.i, !llvm.loop !14

_ZSt13__adjust_heapIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEEliNS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SG_SG_T1_T2_.exit.i.i: ; preds = %while.body.i.i.i.i31, %land.rhs.i.i.i.i, %if.end33.i.i.i
  %__holeIndex.addr.0.lcssa.i.i.i.i28 = phi i64 [ %__holeIndex.addr.1.i.i.i, %if.end33.i.i.i ], [ %__holeIndex.addr.033.i.i.i.i, %land.rhs.i.i.i.i ], [ %__parent.034.i.i.i.i, %while.body.i.i.i.i31 ]
  %add.ptr.i25.i.i.i.i = getelementptr inbounds i32, ptr %__first.coerce, i64 %__holeIndex.addr.0.lcssa.i.i.i.i28
  store i32 %1, ptr %add.ptr.i25.i.i.i.i, align 4, !tbaa !5
  %cmp8.not.i.i = icmp eq i64 %__parent.0.i.i, 0
  %__parent.1.i.i = tail call i64 @llvm.usub.sat.i64(i64 %__parent.0.i.i, i64 1)
  br i1 %cmp8.not.i.i, label %_ZSt13__heap_selectIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SE_SG_.exit, label %while.cond.i.i, !llvm.loop !15

_ZSt13__heap_selectIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SE_SG_.exit: ; preds = %_ZSt13__adjust_heapIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEEliNS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SG_SG_T1_T2_.exit.i.i
  %cmp11.i.i = icmp sgt i64 %sub.ptr.sub.i46.lcssa, 4
  br i1 %cmp11.i.i, label %while.body.i.i, label %while.end

while.body.i.i:                                   ; preds = %_ZSt13__heap_selectIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SE_SG_.exit, %_ZSt10__pop_heapIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SE_SH_.exit.i.i
  %__last.sroa.0.012.i.i = phi ptr [ %incdec.ptr.i.i.i, %_ZSt10__pop_heapIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SE_SH_.exit.i.i ], [ %storemerge44.lcssa, %_ZSt13__heap_selectIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SE_SG_.exit ]
  %incdec.ptr.i.i.i = getelementptr inbounds i8, ptr %__last.sroa.0.012.i.i, i64 -4
  %7 = load i32, ptr %incdec.ptr.i.i.i, align 4, !tbaa !5
  %8 = load i32, ptr %__first.coerce, align 4, !tbaa !5
  store i32 %8, ptr %incdec.ptr.i.i.i, align 4, !tbaa !5
  %sub.ptr.lhs.cast.i.i.i.i = ptrtoint ptr %incdec.ptr.i.i.i to i64
  %sub.ptr.sub.i.i.i.i = sub i64 %sub.ptr.lhs.cast.i.i.i.i, %sub.ptr.rhs.cast.i
  %sub.ptr.div.i.i.i.i = ashr exact i64 %sub.ptr.sub.i.i.i.i, 2
  %sub.i.i.i.i = add nsw i64 %sub.ptr.div.i.i.i.i, -1
  %div.i.i.i.i = sdiv i64 %sub.i.i.i.i, 2
  %cmp62.i.i.i.i = icmp sgt i64 %sub.ptr.div.i.i.i.i, 2
  br i1 %cmp62.i.i.i.i, label %while.body.i.i.i.i, label %while.end.i.i.i.i

while.body.i.i.i.i:                               ; preds = %while.body.i.i, %while.body.i.i.i.i
  %__holeIndex.addr.063.i.i.i.i = phi i64 [ %spec.select.i.i.i.i, %while.body.i.i.i.i ], [ 0, %while.body.i.i ]
  %add.i.i.i.i = shl i64 %__holeIndex.addr.063.i.i.i.i, 1
  %mul.i.i.i.i = add i64 %add.i.i.i.i, 2
  %add.ptr.i.i.i.i.i = getelementptr inbounds i32, ptr %__first.coerce, i64 %mul.i.i.i.i
  %sub3.i.i.i.i = or disjoint i64 %add.i.i.i.i, 1
  %add.ptr.i52.i.i.i.i = getelementptr inbounds i32, ptr %__first.coerce, i64 %sub3.i.i.i.i
  %9 = load i32, ptr %add.ptr.i.i.i.i.i, align 4, !tbaa !5
  %10 = load i32, ptr %add.ptr.i52.i.i.i.i, align 4, !tbaa !5
  %cmp.i.i.i.i.i.i.i.i.i = icmp slt i32 %9, %10
  %spec.select.i.i.i.i = select i1 %cmp.i.i.i.i.i.i.i.i.i, i64 %sub3.i.i.i.i, i64 %mul.i.i.i.i
  %add.ptr.i53.i.i.i.i = getelementptr inbounds i32, ptr %__first.coerce, i64 %spec.select.i.i.i.i
  %11 = load i32, ptr %add.ptr.i53.i.i.i.i, align 4, !tbaa !5
  %add.ptr.i54.i.i.i.i = getelementptr inbounds i32, ptr %__first.coerce, i64 %__holeIndex.addr.063.i.i.i.i
  store i32 %11, ptr %add.ptr.i54.i.i.i.i, align 4, !tbaa !5
  %cmp.i.i.i.i = icmp slt i64 %spec.select.i.i.i.i, %div.i.i.i.i
  br i1 %cmp.i.i.i.i, label %while.body.i.i.i.i, label %while.end.i.i.i.i, !llvm.loop !13

while.end.i.i.i.i:                                ; preds = %while.body.i.i.i.i, %while.body.i.i
  %__holeIndex.addr.0.lcssa.i.i.i.i = phi i64 [ 0, %while.body.i.i ], [ %spec.select.i.i.i.i, %while.body.i.i.i.i ]
  %12 = and i64 %sub.ptr.sub.i.i.i.i, 4
  %cmp16.i.i.i.i = icmp eq i64 %12, 0
  br i1 %cmp16.i.i.i.i, label %land.lhs.true.i.i.i.i, label %if.end33.i.i.i.i

land.lhs.true.i.i.i.i:                            ; preds = %while.end.i.i.i.i
  %sub17.i.i.i.i = add nsw i64 %sub.ptr.div.i.i.i.i, -2
  %div18.i.i.i.i = ashr exact i64 %sub17.i.i.i.i, 1
  %cmp19.i.i.i.i = icmp eq i64 %__holeIndex.addr.0.lcssa.i.i.i.i, %div18.i.i.i.i
  br i1 %cmp19.i.i.i.i, label %if.then20.i.i.i.i, label %if.end33.i.i.i.i

if.then20.i.i.i.i:                                ; preds = %land.lhs.true.i.i.i.i
  %add21.i.i.i.i = shl i64 %__holeIndex.addr.0.lcssa.i.i.i.i, 1
  %sub24.i.i.i.i = or disjoint i64 %add21.i.i.i.i, 1
  %add.ptr.i55.i.i.i.i = getelementptr inbounds i32, ptr %__first.coerce, i64 %sub24.i.i.i.i
  %13 = load i32, ptr %add.ptr.i55.i.i.i.i, align 4, !tbaa !5
  %add.ptr.i56.i.i.i.i = getelementptr inbounds i32, ptr %__first.coerce, i64 %__holeIndex.addr.0.lcssa.i.i.i.i
  store i32 %13, ptr %add.ptr.i56.i.i.i.i, align 4, !tbaa !5
  br label %if.end33.i.i.i.i

if.end33.i.i.i.i:                                 ; preds = %if.then20.i.i.i.i, %land.lhs.true.i.i.i.i, %while.end.i.i.i.i
  %__holeIndex.addr.1.i.i.i.i = phi i64 [ %sub24.i.i.i.i, %if.then20.i.i.i.i ], [ %__holeIndex.addr.0.lcssa.i.i.i.i, %land.lhs.true.i.i.i.i ], [ %__holeIndex.addr.0.lcssa.i.i.i.i, %while.end.i.i.i.i ]
  %cmp32.i.i.i.i.i = icmp sgt i64 %__holeIndex.addr.1.i.i.i.i, 0
  br i1 %cmp32.i.i.i.i.i, label %land.rhs.i.i.i.i.i, label %_ZSt10__pop_heapIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SE_SH_.exit.i.i

land.rhs.i.i.i.i.i:                               ; preds = %if.end33.i.i.i.i, %while.body.i.i.i.i.i
  %__holeIndex.addr.033.i.i.i.i.i = phi i64 [ %__parent.034.i.i.i.i.i, %while.body.i.i.i.i.i ], [ %__holeIndex.addr.1.i.i.i.i, %if.end33.i.i.i.i ]
  %__parent.034.in.i.i.i.i.i = add nsw i64 %__holeIndex.addr.033.i.i.i.i.i, -1
  %__parent.034.i.i.i.i.i = sdiv i64 %__parent.034.in.i.i.i.i.i, 2
  %add.ptr.i.i.i.i.i.i = getelementptr inbounds i32, ptr %__first.coerce, i64 %__parent.034.i.i.i.i.i
  %14 = load i32, ptr %add.ptr.i.i.i.i.i.i, align 4, !tbaa !5
  %cmp.i.i.i.i.i.i.i.i.i.i = icmp slt i32 %14, %7
  br i1 %cmp.i.i.i.i.i.i.i.i.i.i, label %while.body.i.i.i.i.i, label %_ZSt10__pop_heapIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SE_SH_.exit.i.i

while.body.i.i.i.i.i:                             ; preds = %land.rhs.i.i.i.i.i
  %add.ptr.i24.i.i.i.i.i = getelementptr inbounds nuw i32, ptr %__first.coerce, i64 %__holeIndex.addr.033.i.i.i.i.i
  store i32 %14, ptr %add.ptr.i24.i.i.i.i.i, align 4, !tbaa !5
  %cmp.i.i.i.i.i = icmp sgt i64 %__holeIndex.addr.033.i.i.i.i.i, 2
  br i1 %cmp.i.i.i.i.i, label %land.rhs.i.i.i.i.i, label %_ZSt10__pop_heapIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SE_SH_.exit.i.i, !llvm.loop !14

_ZSt10__pop_heapIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SE_SH_.exit.i.i: ; preds = %while.body.i.i.i.i.i, %land.rhs.i.i.i.i.i, %if.end33.i.i.i.i
  %__holeIndex.addr.0.lcssa.i.i.i.i.i = phi i64 [ %__holeIndex.addr.1.i.i.i.i, %if.end33.i.i.i.i ], [ %__holeIndex.addr.033.i.i.i.i.i, %land.rhs.i.i.i.i.i ], [ %__parent.034.i.i.i.i.i, %while.body.i.i.i.i.i ]
  %add.ptr.i25.i.i.i.i.i = getelementptr inbounds i32, ptr %__first.coerce, i64 %__holeIndex.addr.0.lcssa.i.i.i.i.i
  store i32 %7, ptr %add.ptr.i25.i.i.i.i.i, align 4, !tbaa !5
  %cmp.i.i = icmp sgt i64 %sub.ptr.sub.i.i.i.i, 4
  br i1 %cmp.i.i, label %while.body.i.i, label %while.end, !llvm.loop !16

if.end:                                           ; preds = %while.body.lr.ph, %while.body
  %storemerge4461 = phi ptr [ %__first.sroa.0.1.i.i, %while.body ], [ %__last.coerce, %while.body.lr.ph ]
  %__depth_limit.addr.04560 = phi i64 [ %dec, %while.body ], [ %__depth_limit, %while.body.lr.ph ]
  %sub.ptr.div.i4759 = phi i64 [ %sub.ptr.div.i, %while.body ], [ %sub.ptr.div.i42, %while.body.lr.ph ]
  %dec = add nsw i64 %__depth_limit.addr.04560, -1
  %div.i33 = lshr i64 %sub.ptr.div.i4759, 1
  %add.ptr.i.i = getelementptr inbounds nuw i32, ptr %__first.coerce, i64 %div.i33
  %add.ptr.i29.i = getelementptr inbounds i8, ptr %storemerge4461, i64 -4
  %15 = load i32, ptr %add.ptr.i28.i, align 4, !tbaa !5
  %16 = load i32, ptr %add.ptr.i.i, align 4, !tbaa !5
  %cmp.i.i.i.i.i.i.i = icmp slt i32 %15, %16
  %17 = load i32, ptr %add.ptr.i29.i, align 4, !tbaa !5
  br i1 %cmp.i.i.i.i.i.i.i, label %if.then.i.i, label %if.else33.i.i

if.then.i.i:                                      ; preds = %if.end
  %cmp.i.i.i.i.i63.i.i = icmp slt i32 %16, %17
  br i1 %cmp.i.i.i.i.i63.i.i, label %if.then12.i.i, label %if.else.i.i

if.then12.i.i:                                    ; preds = %if.then.i.i
  %18 = load i32, ptr %__first.coerce, align 4, !tbaa !5
  store i32 %16, ptr %__first.coerce, align 4, !tbaa !5
  store i32 %18, ptr %add.ptr.i.i, align 4, !tbaa !5
  br label %while.body.i.i23.preheader

if.else.i.i:                                      ; preds = %if.then.i.i
  %cmp.i.i.i.i.i64.i.i = icmp slt i32 %15, %17
  %19 = load i32, ptr %__first.coerce, align 4, !tbaa !5
  br i1 %cmp.i.i.i.i.i64.i.i, label %if.then22.i.i, label %if.else27.i.i

if.then22.i.i:                                    ; preds = %if.else.i.i
  store i32 %17, ptr %__first.coerce, align 4, !tbaa !5
  store i32 %19, ptr %add.ptr.i29.i, align 4, !tbaa !5
  br label %while.body.i.i23.preheader

if.else27.i.i:                                    ; preds = %if.else.i.i
  store i32 %15, ptr %__first.coerce, align 4, !tbaa !5
  store i32 %19, ptr %add.ptr.i28.i, align 4, !tbaa !5
  br label %while.body.i.i23.preheader

if.else33.i.i:                                    ; preds = %if.end
  %cmp.i.i.i.i.i65.i.i = icmp slt i32 %15, %17
  br i1 %cmp.i.i.i.i.i65.i.i, label %if.then39.i.i, label %if.else44.i.i

if.then39.i.i:                                    ; preds = %if.else33.i.i
  %20 = load i32, ptr %__first.coerce, align 4, !tbaa !5
  store i32 %15, ptr %__first.coerce, align 4, !tbaa !5
  store i32 %20, ptr %add.ptr.i28.i, align 4, !tbaa !5
  br label %while.body.i.i23.preheader

if.else44.i.i:                                    ; preds = %if.else33.i.i
  %cmp.i.i.i.i.i66.i.i = icmp slt i32 %16, %17
  %21 = load i32, ptr %__first.coerce, align 4, !tbaa !5
  br i1 %cmp.i.i.i.i.i66.i.i, label %if.then50.i.i, label %if.else55.i.i

if.then50.i.i:                                    ; preds = %if.else44.i.i
  store i32 %17, ptr %__first.coerce, align 4, !tbaa !5
  store i32 %21, ptr %add.ptr.i29.i, align 4, !tbaa !5
  br label %while.body.i.i23.preheader

if.else55.i.i:                                    ; preds = %if.else44.i.i
  store i32 %16, ptr %__first.coerce, align 4, !tbaa !5
  store i32 %21, ptr %add.ptr.i.i, align 4, !tbaa !5
  br label %while.body.i.i23.preheader

while.body.i.i23.preheader:                       ; preds = %if.else55.i.i, %if.then50.i.i, %if.then39.i.i, %if.else27.i.i, %if.then22.i.i, %if.then12.i.i
  br label %while.body.i.i23

while.body.i.i23:                                 ; preds = %while.body.i.i23.preheader, %if.end.i.i
  %__last.sroa.0.0.i.i = phi ptr [ %__last.sroa.0.1.i.i, %if.end.i.i ], [ %storemerge4461, %while.body.i.i23.preheader ]
  %__first.sroa.0.0.i.i = phi ptr [ %incdec.ptr.i.i.i24, %if.end.i.i ], [ %add.ptr.i28.i, %while.body.i.i23.preheader ]
  %22 = load i32, ptr %__first.coerce, align 4, !tbaa !5
  br label %while.cond3.i.i

while.cond3.i.i:                                  ; preds = %while.cond3.i.i, %while.body.i.i23
  %__first.sroa.0.1.i.i = phi ptr [ %__first.sroa.0.0.i.i, %while.body.i.i23 ], [ %incdec.ptr.i.i.i24, %while.cond3.i.i ]
  %23 = load i32, ptr %__first.sroa.0.1.i.i, align 4, !tbaa !5
  %cmp.i.i.i.i.i.i31.i = icmp slt i32 %23, %22
  %incdec.ptr.i.i.i24 = getelementptr inbounds nuw i8, ptr %__first.sroa.0.1.i.i, i64 4
  br i1 %cmp.i.i.i.i.i.i31.i, label %while.cond3.i.i, label %while.cond10.i.i, !llvm.loop !17

while.cond10.i.i:                                 ; preds = %while.cond3.i.i, %while.cond10.i.i
  %__last.sroa.0.0.pn.i.i = phi ptr [ %__last.sroa.0.1.i.i, %while.cond10.i.i ], [ %__last.sroa.0.0.i.i, %while.cond3.i.i ]
  %__last.sroa.0.1.i.i = getelementptr inbounds i8, ptr %__last.sroa.0.0.pn.i.i, i64 -4
  %24 = load i32, ptr %__last.sroa.0.1.i.i, align 4, !tbaa !5
  %cmp.i.i.i.i.i32.i.i = icmp slt i32 %22, %24
  br i1 %cmp.i.i.i.i.i32.i.i, label %while.cond10.i.i, label %while.end18.i.i, !llvm.loop !18

while.end18.i.i:                                  ; preds = %while.cond10.i.i
  %cmp.lt.i.i.not.i.i = icmp ult ptr %__first.sroa.0.1.i.i, %__last.sroa.0.1.i.i
  br i1 %cmp.lt.i.i.not.i.i, label %if.end.i.i, label %_ZSt27__unguarded_partition_pivotIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEESE_SE_SE_SG_.exit

if.end.i.i:                                       ; preds = %while.end18.i.i
  store i32 %24, ptr %__first.sroa.0.1.i.i, align 4, !tbaa !5
  store i32 %23, ptr %__last.sroa.0.1.i.i, align 4, !tbaa !5
  br label %while.body.i.i23, !llvm.loop !19

_ZSt27__unguarded_partition_pivotIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEESE_SE_SE_SG_.exit: ; preds = %while.end18.i.i
  tail call void @_ZSt16__introsort_loopIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEElNS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG_T1_(ptr nonnull %__first.sroa.0.1.i.i, ptr %storemerge4461, i64 noundef %dec, ptr %__comp.coerce0, ptr %__comp.coerce1)
  %sub.ptr.lhs.cast.i = ptrtoint ptr %__first.sroa.0.1.i.i to i64
  %sub.ptr.sub.i = sub i64 %sub.ptr.lhs.cast.i, %sub.ptr.rhs.cast.i
  %sub.ptr.div.i = ashr exact i64 %sub.ptr.sub.i, 2
  %cmp = icmp sgt i64 %sub.ptr.div.i, 16
  br i1 %cmp, label %while.body, label %while.end, !llvm.loop !12

while.end:                                        ; preds = %_ZSt27__unguarded_partition_pivotIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEESE_SE_SE_SG_.exit, %_ZSt10__pop_heapIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SE_SH_.exit.i.i, %entry, %_ZSt13__heap_selectIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SE_SG_.exit
  ret void
}

; Function Attrs: mustprogress uwtable
define linkonce_odr void @_ZSt22__final_insertion_sortIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG_(ptr %__first.coerce, ptr %__last.coerce, ptr %__comp.coerce0, ptr %__comp.coerce1) local_unnamed_addr #0 comdat personality ptr @__gxx_personality_v0 {
entry:
  %sub.ptr.lhs.cast.i = ptrtoint ptr %__last.coerce to i64
  %sub.ptr.rhs.cast.i = ptrtoint ptr %__first.coerce to i64
  %sub.ptr.sub.i = sub i64 %sub.ptr.lhs.cast.i, %sub.ptr.rhs.cast.i
  %cmp = icmp sgt i64 %sub.ptr.sub.i, 64
  br i1 %cmp, label %if.then, label %if.else

if.then:                                          ; preds = %entry
  %scevgep = getelementptr i8, ptr %__first.coerce, i64 4
  br label %for.body.i

for.body.i:                                       ; preds = %for.inc.i, %if.then
  %__i.sroa.0.042.i.idx = phi i64 [ 4, %if.then ], [ %__i.sroa.0.042.i.add, %for.inc.i ]
  %__first.coerce.pn41.i = phi ptr [ %__first.coerce, %if.then ], [ %__i.sroa.0.042.i.ptr, %for.inc.i ]
  %__i.sroa.0.042.i.ptr = getelementptr inbounds nuw i8, ptr %__first.coerce, i64 %__i.sroa.0.042.i.idx
  %0 = load i32, ptr %__i.sroa.0.042.i.ptr, align 4, !tbaa !5
  %1 = load i32, ptr %__first.coerce, align 4, !tbaa !5
  %cmp.i.i.i.i.i.i = icmp slt i32 %0, %1
  br i1 %cmp.i.i.i.i.i.i, label %if.then9.i, label %if.else.i

if.then9.i:                                       ; preds = %for.body.i
  %cmp.i.i.i.i.i32.i = icmp samesign ugt i64 %__i.sroa.0.042.i.idx, 4
  br i1 %cmp.i.i.i.i.i32.i, label %if.then.i.i.i.i.i.i, label %if.else.i.i.i.i.i.i, !prof !4

if.then.i.i.i.i.i.i:                              ; preds = %if.then9.i
  tail call void @llvm.memmove.p0.p0.i64(ptr noundef nonnull align 4 dereferenceable(1) %scevgep, ptr noundef nonnull align 4 dereferenceable(1) %__first.coerce, i64 %__i.sroa.0.042.i.idx, i1 false)
  br label %for.inc.i

if.else.i.i.i.i.i.i:                              ; preds = %if.then9.i
  %cmp1.i.i.i.i.i.i = icmp eq i64 %__i.sroa.0.042.i.idx, 4
  br i1 %cmp1.i.i.i.i.i.i, label %if.then2.i.i.i.i.i.i, label %for.inc.i

if.then2.i.i.i.i.i.i:                             ; preds = %if.else.i.i.i.i.i.i
  %add.ptr3.i.i.i.i.i.i = getelementptr inbounds nuw i8, ptr %__first.coerce.pn41.i, i64 4
  store i32 %1, ptr %add.ptr3.i.i.i.i.i.i, align 4, !tbaa !5
  br label %for.inc.i

if.else.i:                                        ; preds = %for.body.i
  %2 = load i32, ptr %__first.coerce.pn41.i, align 4, !tbaa !5
  %cmp.i.i.i.i.i15.i.i = icmp slt i32 %0, %2
  br i1 %cmp.i.i.i.i.i15.i.i, label %while.body.i.i, label %for.inc.i

while.body.i.i:                                   ; preds = %if.else.i, %while.body.i.i
  %3 = phi i32 [ %4, %while.body.i.i ], [ %2, %if.else.i ]
  %__next.sroa.0.017.i.i = phi ptr [ %__next.sroa.0.0.i.i, %while.body.i.i ], [ %__first.coerce.pn41.i, %if.else.i ]
  %__last.sroa.0.016.i.i = phi ptr [ %__next.sroa.0.017.i.i, %while.body.i.i ], [ %__i.sroa.0.042.i.ptr, %if.else.i ]
  store i32 %3, ptr %__last.sroa.0.016.i.i, align 4, !tbaa !5
  %__next.sroa.0.0.i.i = getelementptr inbounds i8, ptr %__next.sroa.0.017.i.i, i64 -4
  %4 = load i32, ptr %__next.sroa.0.0.i.i, align 4, !tbaa !5
  %cmp.i.i.i.i.i.i.i = icmp slt i32 %0, %4
  br i1 %cmp.i.i.i.i.i.i.i, label %while.body.i.i, label %for.inc.i, !llvm.loop !20

for.inc.i:                                        ; preds = %while.body.i.i, %if.else.i, %if.then.i.i.i.i.i.i, %if.else.i.i.i.i.i.i, %if.then2.i.i.i.i.i.i
  %__last.sroa.0.0.lcssa.i.i.sink = phi ptr [ %__first.coerce, %if.then2.i.i.i.i.i.i ], [ %__first.coerce, %if.else.i.i.i.i.i.i ], [ %__first.coerce, %if.then.i.i.i.i.i.i ], [ %__i.sroa.0.042.i.ptr, %if.else.i ], [ %__next.sroa.0.017.i.i, %while.body.i.i ]
  store i32 %0, ptr %__last.sroa.0.0.lcssa.i.i.sink, align 4, !tbaa !5
  %__i.sroa.0.042.i.add = add nuw nsw i64 %__i.sroa.0.042.i.idx, 4
  %cmp.i30.i = icmp eq i64 %__i.sroa.0.042.i.add, 64
  br i1 %cmp.i30.i, label %_ZSt16__insertion_sortIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG_.exit, label %for.body.i, !llvm.loop !21

_ZSt16__insertion_sortIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG_.exit: ; preds = %for.inc.i
  %add.ptr.i = getelementptr inbounds nuw i8, ptr %__first.coerce, i64 64
  %cmp.i9.i = icmp eq ptr %add.ptr.i, %__last.coerce
  br i1 %cmp.i9.i, label %if.end, label %for.body.i21

for.body.i21:                                     ; preds = %_ZSt16__insertion_sortIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG_.exit, %_ZSt25__unguarded_linear_insertIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops14_Val_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SG_.exit.i23
  %__i.sroa.0.010.i = phi ptr [ %incdec.ptr.i.i, %_ZSt25__unguarded_linear_insertIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops14_Val_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SG_.exit.i23 ], [ %add.ptr.i, %_ZSt16__insertion_sortIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG_.exit ]
  %5 = load i32, ptr %__i.sroa.0.010.i, align 4, !tbaa !5
  %__next.sroa.0.014.i.i = getelementptr inbounds i8, ptr %__i.sroa.0.010.i, i64 -4
  %6 = load i32, ptr %__next.sroa.0.014.i.i, align 4, !tbaa !5
  %cmp.i.i.i.i.i15.i.i22 = icmp slt i32 %5, %6
  br i1 %cmp.i.i.i.i.i15.i.i22, label %while.body.i.i26, label %_ZSt25__unguarded_linear_insertIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops14_Val_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SG_.exit.i23

while.body.i.i26:                                 ; preds = %for.body.i21, %while.body.i.i26
  %7 = phi i32 [ %8, %while.body.i.i26 ], [ %6, %for.body.i21 ]
  %__next.sroa.0.017.i.i27 = phi ptr [ %__next.sroa.0.0.i.i29, %while.body.i.i26 ], [ %__next.sroa.0.014.i.i, %for.body.i21 ]
  %__last.sroa.0.016.i.i28 = phi ptr [ %__next.sroa.0.017.i.i27, %while.body.i.i26 ], [ %__i.sroa.0.010.i, %for.body.i21 ]
  store i32 %7, ptr %__last.sroa.0.016.i.i28, align 4, !tbaa !5
  %__next.sroa.0.0.i.i29 = getelementptr inbounds i8, ptr %__next.sroa.0.017.i.i27, i64 -4
  %8 = load i32, ptr %__next.sroa.0.0.i.i29, align 4, !tbaa !5
  %cmp.i.i.i.i.i.i.i30 = icmp slt i32 %5, %8
  br i1 %cmp.i.i.i.i.i.i.i30, label %while.body.i.i26, label %_ZSt25__unguarded_linear_insertIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops14_Val_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SG_.exit.i23, !llvm.loop !20

_ZSt25__unguarded_linear_insertIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops14_Val_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SG_.exit.i23: ; preds = %while.body.i.i26, %for.body.i21
  %__last.sroa.0.0.lcssa.i.i24 = phi ptr [ %__i.sroa.0.010.i, %for.body.i21 ], [ %__next.sroa.0.017.i.i27, %while.body.i.i26 ]
  store i32 %5, ptr %__last.sroa.0.0.lcssa.i.i24, align 4, !tbaa !5
  %incdec.ptr.i.i = getelementptr inbounds nuw i8, ptr %__i.sroa.0.010.i, i64 4
  %cmp.i.i25 = icmp eq ptr %incdec.ptr.i.i, %__last.coerce
  br i1 %cmp.i.i25, label %if.end, label %for.body.i21, !llvm.loop !22

if.else:                                          ; preds = %entry
  %cmp.i.i31 = icmp eq ptr %__first.coerce, %__last.coerce
  %__i.sroa.0.039.i33 = getelementptr inbounds nuw i8, ptr %__first.coerce, i64 4
  %cmp.i3040.i34 = icmp eq ptr %__i.sroa.0.039.i33, %__last.coerce
  %or.cond = select i1 %cmp.i.i31, i1 true, i1 %cmp.i3040.i34
  br i1 %or.cond, label %if.end, label %for.body.i37

for.body.i37:                                     ; preds = %if.else, %for.inc.i45
  %__i.sroa.0.042.i38 = phi ptr [ %__i.sroa.0.0.i46, %for.inc.i45 ], [ %__i.sroa.0.039.i33, %if.else ]
  %__first.coerce.pn41.i39 = phi ptr [ %__i.sroa.0.042.i38, %for.inc.i45 ], [ %__first.coerce, %if.else ]
  %9 = load i32, ptr %__i.sroa.0.042.i38, align 4, !tbaa !5
  %10 = load i32, ptr %__first.coerce, align 4, !tbaa !5
  %cmp.i.i.i.i.i.i40 = icmp slt i32 %9, %10
  br i1 %cmp.i.i.i.i.i.i40, label %if.then9.i53, label %if.else.i41

if.then9.i53:                                     ; preds = %for.body.i37
  %sub.ptr.lhs.cast.i.i.i.i.i.i54 = ptrtoint ptr %__i.sroa.0.042.i38 to i64
  %sub.ptr.sub.i.i.i.i.i.i55 = sub i64 %sub.ptr.lhs.cast.i.i.i.i.i.i54, %sub.ptr.rhs.cast.i
  %sub.ptr.div.i.i.i.i.i.i56 = ashr exact i64 %sub.ptr.sub.i.i.i.i.i.i55, 2
  %cmp.i.i.i.i.i32.i57 = icmp sgt i64 %sub.ptr.div.i.i.i.i.i.i56, 1
  br i1 %cmp.i.i.i.i.i32.i57, label %if.then.i.i.i.i.i.i63, label %if.else.i.i.i.i.i.i58, !prof !4

if.then.i.i.i.i.i.i63:                            ; preds = %if.then9.i53
  %add.ptr.i31.i64 = getelementptr inbounds nuw i8, ptr %__first.coerce.pn41.i39, i64 8
  %idx.neg.i.i.i.i.i.i65 = sub nsw i64 0, %sub.ptr.div.i.i.i.i.i.i56
  %add.ptr.i.i.i.i.i.i66 = getelementptr inbounds i32, ptr %add.ptr.i31.i64, i64 %idx.neg.i.i.i.i.i.i65
  tail call void @llvm.memmove.p0.p0.i64(ptr noundef nonnull align 4 dereferenceable(1) %add.ptr.i.i.i.i.i.i66, ptr noundef nonnull align 4 dereferenceable(1) %__first.coerce, i64 %sub.ptr.sub.i.i.i.i.i.i55, i1 false)
  br label %for.inc.i45

if.else.i.i.i.i.i.i58:                            ; preds = %if.then9.i53
  %cmp1.i.i.i.i.i.i59 = icmp eq i64 %sub.ptr.sub.i.i.i.i.i.i55, 4
  br i1 %cmp1.i.i.i.i.i.i59, label %if.then2.i.i.i.i.i.i61, label %for.inc.i45

if.then2.i.i.i.i.i.i61:                           ; preds = %if.else.i.i.i.i.i.i58
  %add.ptr3.i.i.i.i.i.i62 = getelementptr inbounds nuw i8, ptr %__first.coerce.pn41.i39, i64 4
  store i32 %10, ptr %add.ptr3.i.i.i.i.i.i62, align 4, !tbaa !5
  br label %for.inc.i45

if.else.i41:                                      ; preds = %for.body.i37
  %11 = load i32, ptr %__first.coerce.pn41.i39, align 4, !tbaa !5
  %cmp.i.i.i.i.i15.i.i42 = icmp slt i32 %9, %11
  br i1 %cmp.i.i.i.i.i15.i.i42, label %while.body.i.i48, label %for.inc.i45

while.body.i.i48:                                 ; preds = %if.else.i41, %while.body.i.i48
  %12 = phi i32 [ %13, %while.body.i.i48 ], [ %11, %if.else.i41 ]
  %__next.sroa.0.017.i.i49 = phi ptr [ %__next.sroa.0.0.i.i51, %while.body.i.i48 ], [ %__first.coerce.pn41.i39, %if.else.i41 ]
  %__last.sroa.0.016.i.i50 = phi ptr [ %__next.sroa.0.017.i.i49, %while.body.i.i48 ], [ %__i.sroa.0.042.i38, %if.else.i41 ]
  store i32 %12, ptr %__last.sroa.0.016.i.i50, align 4, !tbaa !5
  %__next.sroa.0.0.i.i51 = getelementptr inbounds i8, ptr %__next.sroa.0.017.i.i49, i64 -4
  %13 = load i32, ptr %__next.sroa.0.0.i.i51, align 4, !tbaa !5
  %cmp.i.i.i.i.i.i.i52 = icmp slt i32 %9, %13
  br i1 %cmp.i.i.i.i.i.i.i52, label %while.body.i.i48, label %for.inc.i45, !llvm.loop !20

for.inc.i45:                                      ; preds = %while.body.i.i48, %if.else.i41, %if.then.i.i.i.i.i.i63, %if.else.i.i.i.i.i.i58, %if.then2.i.i.i.i.i.i61
  %__last.sroa.0.0.lcssa.i.i44.sink = phi ptr [ %__first.coerce, %if.then2.i.i.i.i.i.i61 ], [ %__first.coerce, %if.else.i.i.i.i.i.i58 ], [ %__first.coerce, %if.then.i.i.i.i.i.i63 ], [ %__i.sroa.0.042.i38, %if.else.i41 ], [ %__next.sroa.0.017.i.i49, %while.body.i.i48 ]
  store i32 %9, ptr %__last.sroa.0.0.lcssa.i.i44.sink, align 4, !tbaa !5
  %__i.sroa.0.0.i46 = getelementptr inbounds nuw i8, ptr %__i.sroa.0.042.i38, i64 4
  %cmp.i30.i47 = icmp eq ptr %__i.sroa.0.0.i46, %__last.coerce
  br i1 %cmp.i30.i47, label %if.end, label %for.body.i37, !llvm.loop !21

if.end:                                           ; preds = %for.inc.i45, %_ZSt25__unguarded_linear_insertIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops14_Val_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SG_.exit.i23, %if.else, %_ZSt16__insertion_sortIN9__gnu_cxx17__normal_iteratorIPiSt6vectorIiSaIiEEEENS0_5__ops15_Iter_comp_iterIZNSt6ranges8__detail16__make_comp_projINS9_4lessESt8identityEEDaRT_RT0_EUlOSE_OSG_E_EEEvSE_SE_SG_.exit
  ret void
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i64 @llvm.ctlz.i64(i64, i1 immarg) #5

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i64 @llvm.usub.sat.i64(i64, i64) #6

attributes #0 = { mustprogress uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { nobuiltin allocsize(0) "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #4 = { nobuiltin nounwind "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { mustprogress nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #6 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #7 = { builtin allocsize(0) }
attributes #8 = { builtin nounwind }
attributes #9 = { nounwind }

!llvm.linker.options = !{}
!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"uwtable", i32 2}
!3 = !{!"clang version 20.1.8 (CentOS 20.1.8-9.el10_2)"}
!4 = !{!"branch_weights", !"expected", i32 2000, i32 1}
!5 = !{!6, !6, i64 0}
!6 = !{!"int", !7, i64 0}
!7 = !{!"omnipotent char", !8, i64 0}
!8 = !{!"Simple C++ TBAA"}
!9 = distinct !{!9, !10, !11}
!10 = !{!"llvm.loop.mustprogress"}
!11 = !{!"llvm.loop.unroll.disable"}
!12 = distinct !{!12, !10, !11}
!13 = distinct !{!13, !10, !11}
!14 = distinct !{!14, !10, !11}
!15 = distinct !{!15, !10, !11}
!16 = distinct !{!16, !10, !11}
!17 = distinct !{!17, !10, !11}
!18 = distinct !{!18, !10, !11}
!19 = distinct !{!19, !10, !11}
!20 = distinct !{!20, !10, !11}
!21 = distinct !{!21, !10, !11}
!22 = distinct !{!22, !10, !11}
