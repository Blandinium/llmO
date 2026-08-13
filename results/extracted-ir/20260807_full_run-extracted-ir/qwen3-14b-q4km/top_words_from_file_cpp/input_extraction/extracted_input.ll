; ModuleID = '/home/tijl/code/llmO/results/extracted-ir/20260807_full_run-extracted-ir/qwen3-14b-q4km/top_words_from_file_cpp/input_extraction/assemble/input.bc'
source_filename = "/home/tijl/code/llmO/SUT/top_words_from_file.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-redhat-linux-gnu"

%"class.std::basic_ifstream" = type { %"class.std::basic_istream.base", %"class.std::basic_filebuf", %"class.std::basic_ios" }
%"class.std::basic_istream.base" = type { ptr, i64 }
%"class.std::basic_filebuf" = type { %"class.std::basic_streambuf", %union.pthread_mutex_t, %"class.std::__basic_file", i32, %struct.__mbstate_t, %struct.__mbstate_t, %struct.__mbstate_t, ptr, i64, i8, i8, i8, i8, ptr, ptr, i8, ptr, ptr, i64, ptr, ptr }
%"class.std::basic_streambuf" = type { ptr, ptr, ptr, ptr, ptr, ptr, ptr, %"class.std::locale" }
%"class.std::locale" = type { ptr }
%union.pthread_mutex_t = type { %struct.__pthread_mutex_s }
%struct.__pthread_mutex_s = type { i32, i32, i32, i32, i32, i16, i16, %struct.__pthread_internal_list }
%struct.__pthread_internal_list = type { ptr, ptr }
%"class.std::__basic_file" = type <{ ptr, i8, [7 x i8] }>
%struct.__mbstate_t = type { i32, %union.anon.20 }
%union.anon.20 = type { i32 }
%"class.std::basic_ios" = type { %"class.std::ios_base", ptr, i8, i8, ptr, ptr, ptr, ptr }
%"class.std::ios_base" = type { ptr, i64, i64, i32, i32, i32, ptr, %"struct.std::ios_base::_Words", [8 x %"struct.std::ios_base::_Words"], i32, ptr, %"class.std::locale" }
%"struct.std::ios_base::_Words" = type { ptr, i64 }
%"class.std::__cxx11::basic_string" = type { %"struct.std::__cxx11::basic_string<char>::_Alloc_hider", i64, %union.anon }
%"struct.std::__cxx11::basic_string<char>::_Alloc_hider" = type { ptr }
%union.anon = type { i64, [8 x i8] }
%"class.std::allocator.0" = type { i8 }
%"class.std::vector" = type { %"struct.std::_Vector_base" }
%"struct.std::_Vector_base" = type { %"struct.std::_Vector_base<std::__cxx11::basic_string<char>, std::allocator<std::__cxx11::basic_string<char>>>::_Vector_impl" }
%"struct.std::_Vector_base<std::__cxx11::basic_string<char>, std::allocator<std::__cxx11::basic_string<char>>>::_Vector_impl" = type { %"struct.std::_Vector_base<std::__cxx11::basic_string<char>, std::allocator<std::__cxx11::basic_string<char>>>::_Vector_impl_data" }
%"struct.std::_Vector_base<std::__cxx11::basic_string<char>, std::allocator<std::__cxx11::basic_string<char>>>::_Vector_impl_data" = type { ptr, ptr, ptr }
%"class.std::unordered_map" = type { %"class.std::_Hashtable" }
%"class.std::_Hashtable" = type { ptr, i64, %"struct.std::__detail::_Hash_node_base", i64, %"struct.std::__detail::_Prime_rehash_policy", ptr }
%"struct.std::__detail::_Hash_node_base" = type { ptr }
%"struct.std::__detail::_Prime_rehash_policy" = type { float, i64 }
%"class.std::vector.9" = type { %"struct.std::_Vector_base.10" }
%"struct.std::_Vector_base.10" = type { %"struct.std::_Vector_base<std::pair<std::__cxx11::basic_string<char>, unsigned long>, std::allocator<std::pair<std::__cxx11::basic_string<char>, unsigned long>>>::_Vector_impl" }
%"struct.std::_Vector_base<std::pair<std::__cxx11::basic_string<char>, unsigned long>, std::allocator<std::pair<std::__cxx11::basic_string<char>, unsigned long>>>::_Vector_impl" = type { %"struct.std::_Vector_base<std::pair<std::__cxx11::basic_string<char>, unsigned long>, std::allocator<std::pair<std::__cxx11::basic_string<char>, unsigned long>>>::_Vector_impl_data" }
%"struct.std::_Vector_base<std::pair<std::__cxx11::basic_string<char>, unsigned long>, std::allocator<std::pair<std::__cxx11::basic_string<char>, unsigned long>>>::_Vector_impl_data" = type { ptr, ptr, ptr }
%"class.std::unique_ptr" = type { %"struct.std::__uniq_ptr_data" }
%"struct.std::__uniq_ptr_data" = type { %"class.std::__uniq_ptr_impl" }
%"class.std::__uniq_ptr_impl" = type { %"class.std::tuple" }
%"class.std::tuple" = type { %"struct.std::_Tuple_impl" }
%"struct.std::_Tuple_impl" = type { %"struct.std::_Tuple_impl.16", %"struct.std::_Head_base.17" }
%"struct.std::_Tuple_impl.16" = type { %"struct.std::_Head_base" }
%"struct.std::_Head_base" = type { %class.anon }
%class.anon = type { i64 }
%"struct.std::_Head_base.17" = type { ptr }
%struct.WordCount = type { ptr, i64 }
%"struct.std::pair.14" = type { %"class.std::__cxx11::basic_string", i64 }

@.str.2 = external hidden unnamed_addr constant [28 x i8], align 1
@_ZTISt13runtime_error = external constant ptr
@.str.3 = external hidden unnamed_addr constant [38 x i8], align 1
@.str.4 = external hidden unnamed_addr constant [28 x i8], align 1
@_ZTTSt14basic_ifstreamIcSt11char_traitsIcEE = external unnamed_addr constant [4 x ptr], align 8
@.str.6 = external hidden unnamed_addr constant [24 x i8], align 1
@_ZTISt9bad_alloc = external constant ptr
@_ZTVSt9bad_alloc = external unnamed_addr constant { [5 x ptr] }, align 8

; Function Attrs: mustprogress uwtable
define noundef ptr @top_words_from_file(ptr noundef readonly %path, ptr noundef %ignore_words, i64 noundef %ignore_words_length, i64 noundef %max_results, ptr noundef writeonly %result_length) local_unnamed_addr #0 personality ptr @__gxx_personality_v0 {
entry:
  %file.i = alloca %"class.std::basic_ifstream", align 8
  %ref.tmp.i = alloca %"class.std::__cxx11::basic_string", align 8
  %ref.tmp17.i = alloca %"class.std::__cxx11::basic_string", align 8
  %ref.tmp48.i = alloca %"class.std::__cxx11::basic_string", align 8
  %ref.tmp.i.i = alloca %"class.std::allocator.0", align 1
  %ignore = alloca %"class.std::vector", align 8
  %text = alloca %"class.std::__cxx11::basic_string", align 8
  %ref.tmp = alloca %"class.std::__cxx11::basic_string", align 8
  %normalized_ignore = alloca %"class.std::vector", align 8
  %normalized = alloca %"class.std::__cxx11::basic_string", align 8
  %frequencies = alloca %"class.std::unordered_map", align 8
  %agg.tmp = alloca %"class.std::__cxx11::basic_string", align 8
  %frequency_items = alloca %"class.std::vector.9", align 8
  %result_guard = alloca %"class.std::unique_ptr", align 8
  %cmp.not = icmp eq ptr %result_length, null
  br i1 %cmp.not, label %if.end, label %if.then

if.then:                                          ; preds = %entry
  store i64 0, ptr %result_length, align 8, !tbaa !4
  br label %if.end

if.end:                                           ; preds = %if.then, %entry
  %cmp1 = icmp eq ptr %path, null
  br i1 %cmp1, label %return, label %lor.lhs.false

lor.lhs.false:                                    ; preds = %if.end
  %cmp2 = icmp eq ptr %ignore_words, null
  %cmp3 = icmp ne i64 %ignore_words_length, 0
  %or.cond = and i1 %cmp2, %cmp3
  br i1 %or.cond, label %return, label %if.end5

if.end5:                                          ; preds = %lor.lhs.false
  call void @llvm.lifetime.start.p0(i64 24, ptr nonnull %ignore) #20
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 8 dereferenceable(24) %ignore, i8 0, i64 24, i1 false)
  invoke void @_ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EE7reserveEm(ptr noundef nonnull align 8 dereferenceable(24) %ignore, i64 noundef %ignore_words_length)
          to label %for.cond.preheader unwind label %lpad

for.cond.preheader:                               ; preds = %if.end5
  %cmp6382.not = icmp eq i64 %ignore_words_length, 0
  br i1 %cmp6382.not, label %for.cond.cleanup, label %for.body.lr.ph

for.body.lr.ph:                                   ; preds = %for.cond.preheader
  %_M_finish.i = getelementptr inbounds nuw i8, ptr %ignore, i64 8
  %_M_end_of_storage.i = getelementptr inbounds nuw i8, ptr %ignore, i64 16
  br label %for.body

for.cond.cleanup:                                 ; preds = %for.inc, %for.cond.preheader
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %text) #20
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %ref.tmp) #20
  %0 = getelementptr inbounds nuw i8, ptr %ref.tmp, i64 16
  store ptr %0, ptr %ref.tmp, align 8, !tbaa !8
  %call.i.i = call noundef i64 @strlen(ptr noundef nonnull dereferenceable(1) %path) #20
  %cmp.i.i = icmp ugt i64 %call.i.i, 15
  br i1 %cmp.i.i, label %if.then.i.i, label %if.end.i.i

if.then.i.i:                                      ; preds = %for.cond.cleanup
  %cmp.i.i.i = icmp slt i64 %call.i.i, 0
  br i1 %cmp.i.i.i, label %if.then.i.i.i, label %if.end11.i.i.i

if.then.i.i.i:                                    ; preds = %if.then.i.i
  invoke void @_ZSt20__throw_length_errorPKc(ptr noundef nonnull @.str.6) #13
          to label %.noexc217 unwind label %lpad14

.noexc217:                                        ; preds = %if.then.i.i.i
  unreachable

if.end11.i.i.i:                                   ; preds = %if.then.i.i
  %add.i.i.i = add nuw i64 %call.i.i, 1
  %cmp.i.i.i.i.i = icmp slt i64 %add.i.i.i, 0
  br i1 %cmp.i.i.i.i.i, label %if.end.i.i.i.i.i, label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm.exit.i.i, !prof !12

if.end.i.i.i.i.i:                                 ; preds = %if.end11.i.i.i
  invoke void @_ZSt17__throw_bad_allocv() #21
          to label %.noexc218 unwind label %lpad14

.noexc218:                                        ; preds = %if.end.i.i.i.i.i
  unreachable

_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm.exit.i.i: ; preds = %if.end11.i.i.i
  %call5.i.i.i.i11.i219 = invoke noalias noundef nonnull ptr @_Znwm(i64 noundef %add.i.i.i) #22
          to label %call5.i.i.i.i11.i.noexc unwind label %lpad14

call5.i.i.i.i11.i.noexc:                          ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm.exit.i.i
  store ptr %call5.i.i.i.i11.i219, ptr %ref.tmp, align 8, !tbaa !13
  store i64 %call.i.i, ptr %0, align 8, !tbaa !15
  br label %if.end.i.i

if.end.i.i:                                       ; preds = %call5.i.i.i.i11.i.noexc, %for.cond.cleanup
  %1 = load ptr, ptr %ref.tmp, align 8, !tbaa !13
  switch i64 %call.i.i, label %if.end.i.i.i9.i.i [
    i64 1, label %if.then.i.i.i.i
    i64 0, label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC2IS3_EEPKcRKS3_.exit
  ]

if.then.i.i.i.i:                                  ; preds = %if.end.i.i
  %2 = load i8, ptr %path, align 1, !tbaa !15
  store i8 %2, ptr %1, align 1, !tbaa !15
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC2IS3_EEPKcRKS3_.exit

if.end.i.i.i9.i.i:                                ; preds = %if.end.i.i
  call void @llvm.memcpy.p0.p0.i64(ptr align 1 %1, ptr nonnull align 1 %path, i64 %call.i.i, i1 false)
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC2IS3_EEPKcRKS3_.exit

_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC2IS3_EEPKcRKS3_.exit: ; preds = %if.end.i.i.i9.i.i, %if.then.i.i.i.i, %if.end.i.i
  %_M_string_length.i.i.i.i = getelementptr inbounds nuw i8, ptr %ref.tmp, i64 8
  store i64 %call.i.i, ptr %_M_string_length.i.i.i.i, align 8, !tbaa !16
  %3 = load ptr, ptr %ref.tmp, align 8, !tbaa !13
  %arrayidx.i.i.i = getelementptr inbounds nuw i8, ptr %3, i64 %call.i.i
  store i8 0, ptr %arrayidx.i.i.i, align 1, !tbaa !15
  call void @llvm.experimental.noalias.scope.decl(metadata !17)
  call void @llvm.lifetime.start.p0(i64 520, ptr nonnull %file.i) #20, !noalias !17
  invoke void @_ZNSt14basic_ifstreamIcSt11char_traitsIcEEC1ERKNSt7__cxx1112basic_stringIcS1_SaIcEEESt13_Ios_Openmode(ptr noundef nonnull align 8 dereferenceable(256) %file.i, ptr noundef nonnull align 8 dereferenceable(32) %ref.tmp, i32 noundef 4)
          to label %.noexc230 unwind label %lpad16

lpad:                                             ; preds = %if.end5
  %4 = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup180

for.body:                                         ; preds = %for.inc, %for.body.lr.ph
  %i.0383 = phi i64 [ 0, %for.body.lr.ph ], [ %inc, %for.inc ]
  %arrayidx = getelementptr inbounds nuw ptr, ptr %ignore_words, i64 %i.0383
  %5 = load ptr, ptr %arrayidx, align 8, !tbaa !20
  %cmp7.not = icmp eq ptr %5, null
  br i1 %cmp7.not, label %for.inc, label %if.then8

if.then8:                                         ; preds = %for.body
  %6 = load ptr, ptr %_M_finish.i, align 8, !tbaa !21
  %7 = load ptr, ptr %_M_end_of_storage.i, align 8, !tbaa !24
  %cmp.not.i = icmp eq ptr %6, %7
  br i1 %cmp.not.i, label %if.else.i, label %if.then.i220

if.then.i220:                                     ; preds = %if.then8
  call void @llvm.lifetime.start.p0(i64 1, ptr nonnull %ref.tmp.i.i) #20
  invoke void @_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC2IS3_EEPKcRKS3_(ptr noundef nonnull align 8 dereferenceable(32) %6, ptr noundef nonnull %5, ptr noundef nonnull align 1 dereferenceable(1) %ref.tmp.i.i)
          to label %.noexc222 unwind label %lpad10

.noexc222:                                        ; preds = %if.then.i220
  call void @llvm.lifetime.end.p0(i64 1, ptr nonnull %ref.tmp.i.i) #20
  %8 = load ptr, ptr %_M_finish.i, align 8, !tbaa !21
  %incdec.ptr.i = getelementptr inbounds nuw i8, ptr %8, i64 32
  store ptr %incdec.ptr.i, ptr %_M_finish.i, align 8, !tbaa !21
  br label %for.inc

if.else.i:                                        ; preds = %if.then8
  invoke void @_ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EE17_M_realloc_appendIJRKPKcEEEvDpOT_(ptr noundef nonnull align 8 dereferenceable(24) %ignore, ptr noundef nonnull align 8 dereferenceable(8) %arrayidx)
          to label %for.inc unwind label %lpad10

lpad10:                                           ; preds = %if.else.i, %if.then.i220
  %9 = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup180

for.inc:                                          ; preds = %if.else.i, %.noexc222, %for.body
  %inc = add nuw i64 %i.0383, 1
  %exitcond.not = icmp eq i64 %inc, %ignore_words_length
  br i1 %exitcond.not, label %for.cond.cleanup, label %for.body, !llvm.loop !25

.noexc230:                                        ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC2IS3_EEPKcRKS3_.exit
  %vtable.i = load ptr, ptr %file.i, align 8, !tbaa !28, !noalias !17
  %vbase.offset.ptr.i = getelementptr i8, ptr %vtable.i, i64 -24
  %vbase.offset.i = load i64, ptr %vbase.offset.ptr.i, align 8, !noalias !17
  %add.ptr.i = getelementptr inbounds i8, ptr %file.i, i64 %vbase.offset.i
  %_M_streambuf_state.i.i.i.i = getelementptr inbounds nuw i8, ptr %add.ptr.i, i64 32
  %10 = load i32, ptr %_M_streambuf_state.i.i.i.i, align 8, !tbaa !30, !noalias !17
  %and.i.i.i.i = and i32 %10, 5
  %cmp.i.i.not.i = icmp eq i32 %and.i.i.i.i, 0
  br i1 %cmp.i.i.not.i, label %if.end.i228, label %if.then.i224

if.then.i224:                                     ; preds = %.noexc230
  %exception.i = call ptr @__cxa_allocate_exception(i64 16) #20, !noalias !17
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %ref.tmp.i) #20, !noalias !17
  invoke void @_ZStplIcSt11char_traitsIcESaIcEENSt7__cxx1112basic_stringIT_T0_T1_EEPKS5_RKS8_(ptr dead_on_unwind nonnull writable sret(%"class.std::__cxx11::basic_string") align 8 %ref.tmp.i, ptr noundef nonnull @.str.2, ptr noundef nonnull align 8 dereferenceable(32) %ref.tmp)
          to label %invoke.cont2.i unwind label %lpad1.i, !noalias !17

invoke.cont2.i:                                   ; preds = %if.then.i224
  invoke void @_ZNSt13runtime_errorC1ERKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE(ptr noundef nonnull align 8 dereferenceable(16) %exception.i, ptr noundef nonnull align 8 dereferenceable(32) %ref.tmp.i)
          to label %invoke.cont4.i unwind label %lpad3.i, !noalias !17

invoke.cont4.i:                                   ; preds = %invoke.cont2.i
  invoke void @__cxa_throw(ptr nonnull %exception.i, ptr nonnull @_ZTISt13runtime_error, ptr nonnull @_ZNSt13runtime_errorD1Ev) #21
          to label %unreachable.i unwind label %lpad3.i, !noalias !17

lpad.i:                                           ; preds = %if.end.i228
  %11 = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup64.i

lpad1.i:                                          ; preds = %if.then.i224
  %12 = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup.i

lpad3.i:                                          ; preds = %invoke.cont4.i, %invoke.cont2.i
  %cleanup.isactive.0.i = phi i1 [ false, %invoke.cont4.i ], [ true, %invoke.cont2.i ]
  %13 = landingpad { ptr, i32 }
          catch ptr null
  %14 = load ptr, ptr %ref.tmp.i, align 8, !tbaa !13, !noalias !17
  %15 = getelementptr inbounds nuw i8, ptr %ref.tmp.i, i64 16
  %cmp.i.i.i.i = icmp eq ptr %14, %15
  br i1 %cmp.i.i.i.i, label %if.then.i.i.i.i226, label %if.then.i.i.i225

if.then.i.i.i.i226:                               ; preds = %lpad3.i
  %_M_string_length.i.i.i.i227 = getelementptr inbounds nuw i8, ptr %ref.tmp.i, i64 8
  %16 = load i64, ptr %_M_string_length.i.i.i.i227, align 8, !tbaa !16, !noalias !17
  %cmp3.i.i.i.i = icmp ult i64 %16, 16
  call void @llvm.assume(i1 %cmp3.i.i.i.i)
  br label %ehcleanup.i

if.then.i.i.i225:                                 ; preds = %lpad3.i
  %17 = load i64, ptr %15, align 8, !tbaa !15, !noalias !17
  %add.i.i.i.i = add i64 %17, 1
  call void @_ZdlPvm(ptr noundef %14, i64 noundef %add.i.i.i.i) #23, !noalias !17
  br label %ehcleanup.i

ehcleanup.i:                                      ; preds = %if.then.i.i.i225, %if.then.i.i.i.i226, %lpad1.i
  %.pn78.i = phi { ptr, i32 } [ %12, %lpad1.i ], [ %13, %if.then.i.i.i.i226 ], [ %13, %if.then.i.i.i225 ]
  %cleanup.isactive.1.i = phi i1 [ true, %lpad1.i ], [ %cleanup.isactive.0.i, %if.then.i.i.i.i226 ], [ %cleanup.isactive.0.i, %if.then.i.i.i225 ]
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %ref.tmp.i) #20, !noalias !17
  br i1 %cleanup.isactive.1.i, label %cleanup.action.i, label %ehcleanup64.i

cleanup.action.i:                                 ; preds = %ehcleanup.i
  call void @__cxa_free_exception(ptr %exception.i) #20, !noalias !17
  br label %ehcleanup64.i

if.end.i228:                                      ; preds = %.noexc230
  %call7.i = invoke noundef nonnull align 8 dereferenceable(16) ptr @_ZNSi5seekgElSt12_Ios_Seekdir(ptr noundef nonnull align 8 dereferenceable(16) %file.i, i64 noundef 0, i32 noundef 2)
          to label %invoke.cont6.i unwind label %lpad.i, !noalias !17

invoke.cont6.i:                                   ; preds = %if.end.i228
  %call11.i = invoke { i64, i64 } @_ZNSi5tellgEv(ptr noundef nonnull align 8 dereferenceable(16) %file.i)
          to label %invoke.cont10.i unwind label %lpad9.i, !noalias !17

invoke.cont10.i:                                  ; preds = %invoke.cont6.i
  %18 = extractvalue { i64, i64 } %call11.i, 0
  %cmp.i229 = icmp slt i64 %18, 0
  br i1 %cmp.i229, label %if.then15.i, label %if.end29.i

if.then15.i:                                      ; preds = %invoke.cont10.i
  %exception16.i = call ptr @__cxa_allocate_exception(i64 16) #20, !noalias !17
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %ref.tmp17.i) #20, !noalias !17
  invoke void @_ZStplIcSt11char_traitsIcESaIcEENSt7__cxx1112basic_stringIT_T0_T1_EEPKS5_RKS8_(ptr dead_on_unwind nonnull writable sret(%"class.std::__cxx11::basic_string") align 8 %ref.tmp17.i, ptr noundef nonnull @.str.3, ptr noundef nonnull align 8 dereferenceable(32) %ref.tmp)
          to label %invoke.cont19.i unwind label %lpad18.i, !noalias !17

invoke.cont19.i:                                  ; preds = %if.then15.i
  invoke void @_ZNSt13runtime_errorC1ERKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE(ptr noundef nonnull align 8 dereferenceable(16) %exception16.i, ptr noundef nonnull align 8 dereferenceable(32) %ref.tmp17.i)
          to label %invoke.cont21.i unwind label %lpad20.i, !noalias !17

invoke.cont21.i:                                  ; preds = %invoke.cont19.i
  invoke void @__cxa_throw(ptr nonnull %exception16.i, ptr nonnull @_ZTISt13runtime_error, ptr nonnull @_ZNSt13runtime_errorD1Ev) #21
          to label %unreachable.i unwind label %lpad20.i, !noalias !17

lpad9.i:                                          ; preds = %invoke.cont6.i
  %19 = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup64.i

lpad18.i:                                         ; preds = %if.then15.i
  %20 = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup24.i

lpad20.i:                                         ; preds = %invoke.cont21.i, %invoke.cont19.i
  %cleanup.isactive22.0.i = phi i1 [ false, %invoke.cont21.i ], [ true, %invoke.cont19.i ]
  %21 = landingpad { ptr, i32 }
          catch ptr null
  %22 = load ptr, ptr %ref.tmp17.i, align 8, !tbaa !13, !noalias !17
  %23 = getelementptr inbounds nuw i8, ptr %ref.tmp17.i, i64 16
  %cmp.i.i.i81.i = icmp eq ptr %22, %23
  br i1 %cmp.i.i.i81.i, label %if.then.i.i.i84.i, label %if.then.i.i82.i

if.then.i.i.i84.i:                                ; preds = %lpad20.i
  %_M_string_length.i.i.i85.i = getelementptr inbounds nuw i8, ptr %ref.tmp17.i, i64 8
  %24 = load i64, ptr %_M_string_length.i.i.i85.i, align 8, !tbaa !16, !noalias !17
  %cmp3.i.i.i86.i = icmp ult i64 %24, 16
  call void @llvm.assume(i1 %cmp3.i.i.i86.i)
  br label %ehcleanup24.i

if.then.i.i82.i:                                  ; preds = %lpad20.i
  %25 = load i64, ptr %23, align 8, !tbaa !15, !noalias !17
  %add.i.i.i83.i = add i64 %25, 1
  call void @_ZdlPvm(ptr noundef %22, i64 noundef %add.i.i.i83.i) #23, !noalias !17
  br label %ehcleanup24.i

ehcleanup24.i:                                    ; preds = %if.then.i.i82.i, %if.then.i.i.i84.i, %lpad18.i
  %.pn75.i = phi { ptr, i32 } [ %20, %lpad18.i ], [ %21, %if.then.i.i.i84.i ], [ %21, %if.then.i.i82.i ]
  %cleanup.isactive22.1.i = phi i1 [ true, %lpad18.i ], [ %cleanup.isactive22.0.i, %if.then.i.i.i84.i ], [ %cleanup.isactive22.0.i, %if.then.i.i82.i ]
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %ref.tmp17.i) #20, !noalias !17
  br i1 %cleanup.isactive22.1.i, label %cleanup.action27.i, label %ehcleanup64.i

cleanup.action27.i:                               ; preds = %ehcleanup24.i
  call void @__cxa_free_exception(ptr %exception16.i) #20, !noalias !17
  br label %ehcleanup64.i

if.end29.i:                                       ; preds = %invoke.cont10.i
  %call32.i = invoke noundef nonnull align 8 dereferenceable(16) ptr @_ZNSi5seekgElSt12_Ios_Seekdir(ptr noundef nonnull align 8 dereferenceable(16) %file.i, i64 noundef 0, i32 noundef 0)
          to label %invoke.cont31.i unwind label %lpad30.i, !noalias !17

invoke.cont31.i:                                  ; preds = %if.end29.i
  %26 = getelementptr inbounds nuw i8, ptr %text, i64 16
  store ptr %26, ptr %text, align 8, !tbaa !8, !alias.scope !17
  %_M_string_length.i.i.i88.i = getelementptr inbounds nuw i8, ptr %text, i64 8
  store i64 0, ptr %_M_string_length.i.i.i88.i, align 8, !tbaa !16, !alias.scope !17
  store i8 0, ptr %26, align 8, !tbaa !15, !alias.scope !17
  %cond.i = icmp eq i64 %18, 0
  br i1 %cond.i, label %_ZL15read_whole_fileRKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE.exit, label %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i.i.i.i.i

_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i.i.i.i.i: ; preds = %invoke.cont31.i
  %cmp.not.i.i.i.i.i = icmp ugt i64 %18, 15
  br i1 %cmp.not.i.i.i.i.i, label %if.else.i.i.i.i.i, label %if.then12.i.i.i.i.i

if.else.i.i.i.i.i:                                ; preds = %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i.i.i.i.i
  invoke void @_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_mutateEmmPKcm(ptr noundef nonnull align 8 dereferenceable(32) %text, i64 noundef 0, i64 noundef 0, ptr noundef null, i64 noundef %18)
          to label %if.then12.i.i.i.i.i unwind label %lpad33.i

if.then12.i.i.i.i.i:                              ; preds = %if.else.i.i.i.i.i, %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i.i.i.i.i
  %27 = load ptr, ptr %text, align 8, !tbaa !13, !alias.scope !17
  %cond.i.i.i.i.i = icmp eq i64 %18, 1
  br i1 %cond.i.i.i.i.i, label %if.then.i36.i.i.i.i.i, label %if.end.i.i37.i.i.i.i.i

if.then.i36.i.i.i.i.i:                            ; preds = %if.then12.i.i.i.i.i
  store i8 0, ptr %27, align 1, !tbaa !15
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE6appendEmc.exit.i.i.i

if.end.i.i37.i.i.i.i.i:                           ; preds = %if.then12.i.i.i.i.i
  call void @llvm.memset.p0.i64(ptr align 1 %27, i8 0, i64 %18, i1 false)
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE6appendEmc.exit.i.i.i

_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE6appendEmc.exit.i.i.i: ; preds = %if.end.i.i37.i.i.i.i.i, %if.then.i36.i.i.i.i.i
  store i64 %18, ptr %_M_string_length.i.i.i88.i, align 8, !tbaa !16, !alias.scope !17
  %28 = load ptr, ptr %text, align 8, !tbaa !13, !alias.scope !17
  %arrayidx.i.i.i.i.i.i = getelementptr inbounds nuw i8, ptr %28, i64 %18
  store i8 0, ptr %arrayidx.i.i.i.i.i.i, align 1, !tbaa !15
  %29 = load ptr, ptr %text, align 8, !tbaa !13, !alias.scope !17
  %call39.i = invoke noundef nonnull align 8 dereferenceable(16) ptr @_ZNSi4readEPcl(ptr noundef nonnull align 8 dereferenceable(16) %file.i, ptr noundef %29, i64 noundef %18)
          to label %invoke.cont38.i unwind label %lpad33.i

invoke.cont38.i:                                  ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE6appendEmc.exit.i.i.i
  %vtable40.i = load ptr, ptr %file.i, align 8, !tbaa !28, !noalias !17
  %vbase.offset.ptr41.i = getelementptr i8, ptr %vtable40.i, i64 -24
  %vbase.offset42.i = load i64, ptr %vbase.offset.ptr41.i, align 8
  %add.ptr43.i = getelementptr inbounds i8, ptr %file.i, i64 %vbase.offset42.i
  %_M_streambuf_state.i.i.i93.i = getelementptr inbounds nuw i8, ptr %add.ptr43.i, i64 32
  %30 = load i32, ptr %_M_streambuf_state.i.i.i93.i, align 8, !tbaa !30, !noalias !17
  %and.i.i.i94.i = and i32 %30, 5
  %cmp.i.i95.not.i = icmp eq i32 %and.i.i.i94.i, 0
  br i1 %cmp.i.i95.not.i, label %_ZL15read_whole_fileRKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE.exit, label %if.then46.i

if.then46.i:                                      ; preds = %invoke.cont38.i
  %exception47.i = call ptr @__cxa_allocate_exception(i64 16) #20
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %ref.tmp48.i) #20, !noalias !17
  invoke void @_ZStplIcSt11char_traitsIcESaIcEENSt7__cxx1112basic_stringIT_T0_T1_EEPKS5_RKS8_(ptr dead_on_unwind nonnull writable sret(%"class.std::__cxx11::basic_string") align 8 %ref.tmp48.i, ptr noundef nonnull @.str.4, ptr noundef nonnull align 8 dereferenceable(32) %ref.tmp)
          to label %invoke.cont50.i unwind label %lpad49.i

invoke.cont50.i:                                  ; preds = %if.then46.i
  invoke void @_ZNSt13runtime_errorC1ERKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE(ptr noundef nonnull align 8 dereferenceable(16) %exception47.i, ptr noundef nonnull align 8 dereferenceable(32) %ref.tmp48.i)
          to label %invoke.cont52.i unwind label %lpad51.i

invoke.cont52.i:                                  ; preds = %invoke.cont50.i
  invoke void @__cxa_throw(ptr nonnull %exception47.i, ptr nonnull @_ZTISt13runtime_error, ptr nonnull @_ZNSt13runtime_errorD1Ev) #21
          to label %unreachable.i unwind label %lpad51.i

lpad30.i:                                         ; preds = %if.end29.i
  %31 = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup64.i

lpad33.i:                                         ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE6appendEmc.exit.i.i.i, %if.else.i.i.i.i.i
  %32 = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup62.i

lpad49.i:                                         ; preds = %if.then46.i
  %33 = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup55.i

lpad51.i:                                         ; preds = %invoke.cont52.i, %invoke.cont50.i
  %cleanup.isactive53.0.i = phi i1 [ false, %invoke.cont52.i ], [ true, %invoke.cont50.i ]
  %34 = landingpad { ptr, i32 }
          catch ptr null
  %35 = load ptr, ptr %ref.tmp48.i, align 8, !tbaa !13, !noalias !17
  %36 = getelementptr inbounds nuw i8, ptr %ref.tmp48.i, i64 16
  %cmp.i.i.i96.i = icmp eq ptr %35, %36
  br i1 %cmp.i.i.i96.i, label %if.then.i.i.i99.i, label %if.then.i.i97.i

if.then.i.i.i99.i:                                ; preds = %lpad51.i
  %_M_string_length.i.i.i100.i = getelementptr inbounds nuw i8, ptr %ref.tmp48.i, i64 8
  %37 = load i64, ptr %_M_string_length.i.i.i100.i, align 8, !tbaa !16, !noalias !17
  %cmp3.i.i.i101.i = icmp ult i64 %37, 16
  call void @llvm.assume(i1 %cmp3.i.i.i101.i)
  br label %ehcleanup55.i

if.then.i.i97.i:                                  ; preds = %lpad51.i
  %38 = load i64, ptr %36, align 8, !tbaa !15, !noalias !17
  %add.i.i.i98.i = add i64 %38, 1
  call void @_ZdlPvm(ptr noundef %35, i64 noundef %add.i.i.i98.i) #23
  br label %ehcleanup55.i

ehcleanup55.i:                                    ; preds = %if.then.i.i97.i, %if.then.i.i.i99.i, %lpad49.i
  %.pn.i = phi { ptr, i32 } [ %33, %lpad49.i ], [ %34, %if.then.i.i.i99.i ], [ %34, %if.then.i.i97.i ]
  %cleanup.isactive53.1.i = phi i1 [ true, %lpad49.i ], [ %cleanup.isactive53.0.i, %if.then.i.i.i99.i ], [ %cleanup.isactive53.0.i, %if.then.i.i97.i ]
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %ref.tmp48.i) #20, !noalias !17
  br i1 %cleanup.isactive53.1.i, label %cleanup.action58.i, label %ehcleanup62.i

cleanup.action58.i:                               ; preds = %ehcleanup55.i
  call void @__cxa_free_exception(ptr %exception47.i) #20
  br label %ehcleanup62.i

ehcleanup62.i:                                    ; preds = %cleanup.action58.i, %ehcleanup55.i, %lpad33.i
  %.pn.pn.i = phi { ptr, i32 } [ %.pn.i, %cleanup.action58.i ], [ %.pn.i, %ehcleanup55.i ], [ %32, %lpad33.i ]
  %39 = load ptr, ptr %text, align 8, !tbaa !13, !alias.scope !17
  %cmp.i.i.i103.i = icmp eq ptr %39, %26
  br i1 %cmp.i.i.i103.i, label %if.then.i.i.i106.i, label %if.then.i.i104.i

if.then.i.i.i106.i:                               ; preds = %ehcleanup62.i
  %40 = load i64, ptr %_M_string_length.i.i.i88.i, align 8, !tbaa !16, !alias.scope !17
  %cmp3.i.i.i108.i = icmp ult i64 %40, 16
  call void @llvm.assume(i1 %cmp3.i.i.i108.i)
  br label %ehcleanup64.i

if.then.i.i104.i:                                 ; preds = %ehcleanup62.i
  %41 = load i64, ptr %26, align 8, !tbaa !15, !alias.scope !17
  %add.i.i.i105.i = add i64 %41, 1
  call void @_ZdlPvm(ptr noundef %39, i64 noundef %add.i.i.i105.i) #23
  br label %ehcleanup64.i

ehcleanup64.i:                                    ; preds = %if.then.i.i104.i, %if.then.i.i.i106.i, %lpad30.i, %cleanup.action27.i, %ehcleanup24.i, %lpad9.i, %cleanup.action.i, %ehcleanup.i, %lpad.i
  %.pn78.pn.i = phi { ptr, i32 } [ %.pn78.i, %cleanup.action.i ], [ %.pn78.i, %ehcleanup.i ], [ %11, %lpad.i ], [ %.pn75.i, %cleanup.action27.i ], [ %.pn75.i, %ehcleanup24.i ], [ %31, %lpad30.i ], [ %19, %lpad9.i ], [ %.pn.pn.i, %if.then.i.i.i106.i ], [ %.pn.pn.i, %if.then.i.i104.i ]
  call void @_ZNSt14basic_ifstreamIcSt11char_traitsIcEED2Ev(ptr noundef nonnull align 8 dereferenceable(256) %file.i, ptr noundef nonnull @_ZTTSt14basic_ifstreamIcSt11char_traitsIcEE) #20
  %42 = getelementptr inbounds nuw i8, ptr %file.i, i64 256
  call void @_ZNSt8ios_baseD2Ev(ptr noundef nonnull align 8 dereferenceable(264) %42) #20
  call void @llvm.lifetime.end.p0(i64 520, ptr nonnull %file.i) #20, !noalias !17
  br label %lpad16.body

unreachable.i:                                    ; preds = %invoke.cont52.i, %invoke.cont21.i, %invoke.cont4.i
  unreachable

_ZL15read_whole_fileRKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE.exit: ; preds = %invoke.cont38.i, %invoke.cont31.i
  call void @_ZNSt14basic_ifstreamIcSt11char_traitsIcEED2Ev(ptr noundef nonnull align 8 dereferenceable(256) %file.i, ptr noundef nonnull @_ZTTSt14basic_ifstreamIcSt11char_traitsIcEE) #20
  %43 = getelementptr inbounds nuw i8, ptr %file.i, i64 256
  call void @_ZNSt8ios_baseD2Ev(ptr noundef nonnull align 8 dereferenceable(264) %43) #20
  call void @llvm.lifetime.end.p0(i64 520, ptr nonnull %file.i) #20, !noalias !17
  %44 = load ptr, ptr %ref.tmp, align 8, !tbaa !13
  %cmp.i.i.i231 = icmp eq ptr %44, %0
  br i1 %cmp.i.i.i231, label %if.then.i.i.i234, label %if.then.i.i232

if.then.i.i.i234:                                 ; preds = %_ZL15read_whole_fileRKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE.exit
  %45 = load i64, ptr %_M_string_length.i.i.i.i, align 8, !tbaa !16
  %cmp3.i.i.i = icmp ult i64 %45, 16
  call void @llvm.assume(i1 %cmp3.i.i.i)
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit

if.then.i.i232:                                   ; preds = %_ZL15read_whole_fileRKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE.exit
  %46 = load i64, ptr %0, align 8, !tbaa !15
  %add.i.i.i233 = add i64 %46, 1
  call void @_ZdlPvm(ptr noundef %44, i64 noundef %add.i.i.i233) #23
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit

_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit: ; preds = %if.then.i.i232, %if.then.i.i.i234
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %ref.tmp) #20
  call void @llvm.lifetime.start.p0(i64 24, ptr nonnull %normalized_ignore) #20
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 8 dereferenceable(24) %normalized_ignore, i8 0, i64 24, i1 false)
  %47 = load ptr, ptr %ignore, align 8, !tbaa !40
  %_M_finish.i235 = getelementptr inbounds nuw i8, ptr %ignore, i64 8
  %48 = load ptr, ptr %_M_finish.i235, align 8, !tbaa !40
  %cmp.i236386 = icmp eq ptr %47, %48
  br i1 %cmp.i236386, label %for.cond.cleanup25, label %for.body26.lr.ph

for.body26.lr.ph:                                 ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit
  %49 = getelementptr inbounds nuw i8, ptr %normalized, i64 16
  %_M_string_length.i.i.i245 = getelementptr inbounds nuw i8, ptr %normalized, i64 8
  %_M_finish.i.i = getelementptr inbounds nuw i8, ptr %normalized_ignore, i64 8
  %_M_end_of_storage.i.i = getelementptr inbounds nuw i8, ptr %normalized_ignore, i64 16
  br label %for.body26

for.cond.cleanup25:                               ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit269, %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit
  call void @llvm.lifetime.start.p0(i64 56, ptr nonnull %frequencies) #20
  %_M_single_bucket.i.i = getelementptr inbounds nuw i8, ptr %frequencies, i64 48
  store ptr %_M_single_bucket.i.i, ptr %frequencies, align 8, !tbaa !41
  %_M_bucket_count.i.i = getelementptr inbounds nuw i8, ptr %frequencies, i64 8
  store i64 1, ptr %_M_bucket_count.i.i, align 8, !tbaa !48
  %_M_before_begin.i.i = getelementptr inbounds nuw i8, ptr %frequencies, i64 16
  %_M_rehash_policy.i.i = getelementptr inbounds nuw i8, ptr %frequencies, i64 32
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %_M_before_begin.i.i, i8 0, i64 16, i1 false)
  store float 1.000000e+00, ptr %_M_rehash_policy.i.i, align 8, !tbaa !49
  %_M_next_resize.i.i.i = getelementptr inbounds nuw i8, ptr %frequencies, i64 40
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %_M_next_resize.i.i.i, i8 0, i64 16, i1 false)
  %50 = getelementptr inbounds nuw i8, ptr %agg.tmp, i64 16
  store ptr %50, ptr %agg.tmp, align 8, !tbaa !8
  %_M_string_length.i.i.i237 = getelementptr inbounds nuw i8, ptr %agg.tmp, i64 8
  store i64 0, ptr %_M_string_length.i.i.i237, align 8, !tbaa !16
  store i8 0, ptr %50, align 8, !tbaa !15
  invoke fastcc void @_ZL24scan_text_tail_recursiveRKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmS4_RSt13unordered_mapIS4_mSt4hashIS4_ESt8equal_toIS4_ESaISt4pairIS5_mEEERKSt6vectorIS4_SaIS4_EE(ptr noundef nonnull align 8 dereferenceable(32) %text, i64 noundef 0, ptr noundef %agg.tmp, ptr noundef nonnull align 8 dereferenceable(56) %frequencies, ptr noundef nonnull align 8 dereferenceable(24) %normalized_ignore)
          to label %invoke.cont70 unwind label %lpad69

lpad14:                                           ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm.exit.i.i, %if.end.i.i.i.i.i, %if.then.i.i.i
  %51 = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup

lpad16:                                           ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC2IS3_EEPKcRKS3_.exit
  %52 = landingpad { ptr, i32 }
          catch ptr null
  br label %lpad16.body

lpad16.body:                                      ; preds = %lpad16, %ehcleanup64.i
  %eh.lpad-body = phi { ptr, i32 } [ %52, %lpad16 ], [ %.pn78.pn.i, %ehcleanup64.i ]
  %53 = load ptr, ptr %ref.tmp, align 8, !tbaa !13
  %cmp.i.i.i238 = icmp eq ptr %53, %0
  br i1 %cmp.i.i.i238, label %if.then.i.i.i241, label %if.then.i.i239

if.then.i.i.i241:                                 ; preds = %lpad16.body
  %54 = load i64, ptr %_M_string_length.i.i.i.i, align 8, !tbaa !16
  %cmp3.i.i.i243 = icmp ult i64 %54, 16
  call void @llvm.assume(i1 %cmp3.i.i.i243)
  br label %ehcleanup

if.then.i.i239:                                   ; preds = %lpad16.body
  %55 = load i64, ptr %0, align 8, !tbaa !15
  %add.i.i.i240 = add i64 %55, 1
  call void @_ZdlPvm(ptr noundef %53, i64 noundef %add.i.i.i240) #23
  br label %ehcleanup

ehcleanup:                                        ; preds = %if.then.i.i239, %if.then.i.i.i241, %lpad14
  %.pn = phi { ptr, i32 } [ %51, %lpad14 ], [ %eh.lpad-body, %if.then.i.i.i241 ], [ %eh.lpad-body, %if.then.i.i239 ]
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %ref.tmp) #20
  br label %ehcleanup178

for.body26:                                       ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit269, %for.body26.lr.ph
  %__begin2.sroa.0.0387 = phi ptr [ %47, %for.body26.lr.ph ], [ %incdec.ptr.i270, %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit269 ]
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %normalized) #20
  store ptr %49, ptr %normalized, align 8, !tbaa !8
  store i64 0, ptr %_M_string_length.i.i.i245, align 8, !tbaa !16
  store i8 0, ptr %49, align 8, !tbaa !15
  %_M_string_length.i = getelementptr inbounds nuw i8, ptr %__begin2.sroa.0.0387, i64 8
  %56 = load i64, ptr %_M_string_length.i, align 8, !tbaa !16
  invoke void @_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE7reserveEm(ptr noundef nonnull align 8 dereferenceable(32) %normalized, i64 noundef %56)
          to label %invoke.cont30 unwind label %lpad29

invoke.cont30:                                    ; preds = %for.body26
  %57 = load ptr, ptr %__begin2.sroa.0.0387, align 8, !tbaa !13
  %58 = load i64, ptr %_M_string_length.i, align 8, !tbaa !16
  %add.ptr.i246 = getelementptr inbounds nuw i8, ptr %57, i64 %58
  %cmp.i247384 = icmp samesign eq i64 %58, 0
  br i1 %cmp.i247384, label %for.cond.cleanup38, label %for.body39

for.cond.cleanup38:                               ; preds = %if.end48, %invoke.cont30
  %59 = load i64, ptr %_M_string_length.i.i.i245, align 8, !tbaa !16
  %cmp.i249 = icmp eq i64 %59, 0
  br i1 %cmp.i249, label %if.end59, label %if.then57

lpad29:                                           ; preds = %if.else.i.i, %for.body26
  %60 = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup60

for.body39:                                       ; preds = %if.end48, %invoke.cont30
  %__begin3.sroa.0.0385 = phi ptr [ %incdec.ptr.i258, %if.end48 ], [ %57, %invoke.cont30 ]
  %61 = load i8, ptr %__begin3.sroa.0.0385, align 1, !tbaa !15
  %call43 = invoke noundef zeroext i1 @_Z12is_word_charc(i8 noundef signext %61)
          to label %invoke.cont42 unwind label %lpad41

invoke.cont42:                                    ; preds = %for.body39
  br i1 %call43, label %if.then44, label %if.end48

if.then44:                                        ; preds = %invoke.cont42
  %call46 = invoke noundef signext i8 @_Z14normalize_charc(i8 noundef signext %61)
          to label %invoke.cont45 unwind label %lpad41

invoke.cont45:                                    ; preds = %if.then44
  %62 = load i64, ptr %_M_string_length.i.i.i245, align 8, !tbaa !16
  %add.i = add i64 %62, 1
  %63 = load ptr, ptr %normalized, align 8, !tbaa !13
  %cmp.i.i.i251 = icmp eq ptr %63, %49
  br i1 %cmp.i.i.i251, label %if.then.i.i.i255, label %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i

if.then.i.i.i255:                                 ; preds = %invoke.cont45
  %cmp3.i.i.i256 = icmp ult i64 %62, 16
  call void @llvm.assume(i1 %cmp3.i.i.i256)
  br label %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i

_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i: ; preds = %if.then.i.i.i255, %invoke.cont45
  %64 = load i64, ptr %49, align 8
  %cond.i.i = select i1 %cmp.i.i.i251, i64 15, i64 %64
  %cmp.i252 = icmp ugt i64 %add.i, %cond.i.i
  br i1 %cmp.i252, label %if.then.i254, label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9push_backEc.exit

if.then.i254:                                     ; preds = %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i
  invoke void @_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_mutateEmmPKcm(ptr noundef nonnull align 8 dereferenceable(32) %normalized, i64 noundef %62, i64 noundef 0, ptr noundef null, i64 noundef 1)
          to label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9push_backEc.exit unwind label %lpad41

_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9push_backEc.exit: ; preds = %if.then.i254, %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit.i
  %65 = load ptr, ptr %normalized, align 8, !tbaa !13
  %arrayidx.i = getelementptr inbounds nuw i8, ptr %65, i64 %62
  store i8 %call46, ptr %arrayidx.i, align 1, !tbaa !15
  store i64 %add.i, ptr %_M_string_length.i.i.i245, align 8, !tbaa !16
  %66 = load ptr, ptr %normalized, align 8, !tbaa !13
  %arrayidx.i.i = getelementptr inbounds nuw i8, ptr %66, i64 %add.i
  store i8 0, ptr %arrayidx.i.i, align 1, !tbaa !15
  br label %if.end48

lpad41:                                           ; preds = %if.then.i254, %if.then44, %for.body39
  %67 = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup60

if.end48:                                         ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9push_backEc.exit, %invoke.cont42
  %incdec.ptr.i258 = getelementptr inbounds nuw i8, ptr %__begin3.sroa.0.0385, i64 1
  %cmp.i247 = icmp eq ptr %incdec.ptr.i258, %add.ptr.i246
  br i1 %cmp.i247, label %for.cond.cleanup38, label %for.body39, !llvm.loop !50

if.then57:                                        ; preds = %for.cond.cleanup38
  %68 = load ptr, ptr %_M_finish.i.i, align 8, !tbaa !21
  %69 = load ptr, ptr %_M_end_of_storage.i.i, align 8, !tbaa !24
  %cmp.not.i.i = icmp eq ptr %68, %69
  br i1 %cmp.not.i.i, label %if.else.i.i, label %if.then.i.i259

if.then.i.i259:                                   ; preds = %if.then57
  %70 = getelementptr inbounds nuw i8, ptr %68, i64 16
  store ptr %70, ptr %68, align 8, !tbaa !8
  %71 = load ptr, ptr %normalized, align 8, !tbaa !13
  %cmp.i.i.i.i.i260 = icmp eq ptr %71, %49
  br i1 %cmp.i.i.i.i.i260, label %if.then.i.i.i.i.i, label %if.else.i.i.i.i

if.then.i.i.i.i.i:                                ; preds = %if.then.i.i259
  %cmp3.i.i.i.i.i = icmp ult i64 %59, 16
  call void @llvm.assume(i1 %cmp3.i.i.i.i.i)
  %add.i.i.i.i261 = add nuw nsw i64 %59, 1
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(1) %70, ptr noundef nonnull align 8 dereferenceable(1) %49, i64 %add.i.i.i.i261, i1 false)
  br label %_ZSt12construct_atINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEJS5_EEDTgsnwcvPvLi0E_T_pispclsr3stdE7declvalIT0_EEEEPS7_DpOS8_.exit.i.i

if.else.i.i.i.i:                                  ; preds = %if.then.i.i259
  store ptr %71, ptr %68, align 8, !tbaa !13
  %72 = load i64, ptr %49, align 8, !tbaa !15
  store i64 %72, ptr %70, align 8, !tbaa !15
  br label %_ZSt12construct_atINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEJS5_EEDTgsnwcvPvLi0E_T_pispclsr3stdE7declvalIT0_EEEEPS7_DpOS8_.exit.i.i

_ZSt12construct_atINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEJS5_EEDTgsnwcvPvLi0E_T_pispclsr3stdE7declvalIT0_EEEEPS7_DpOS8_.exit.i.i: ; preds = %if.else.i.i.i.i, %if.then.i.i.i.i.i
  %_M_string_length.i32.i.i.i.i = getelementptr inbounds nuw i8, ptr %68, i64 8
  store i64 %59, ptr %_M_string_length.i32.i.i.i.i, align 8, !tbaa !16
  store ptr %49, ptr %normalized, align 8, !tbaa !13
  store i64 0, ptr %_M_string_length.i.i.i245, align 8, !tbaa !16
  store i8 0, ptr %49, align 8, !tbaa !15
  %incdec.ptr.i.i = getelementptr inbounds nuw i8, ptr %68, i64 32
  store ptr %incdec.ptr.i.i, ptr %_M_finish.i.i, align 8, !tbaa !21
  br label %if.end59

if.else.i.i:                                      ; preds = %if.then57
  invoke void @_ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EE17_M_realloc_appendIJS5_EEEvDpOT_(ptr noundef nonnull align 8 dereferenceable(24) %normalized_ignore, ptr noundef nonnull align 8 dereferenceable(32) %normalized)
          to label %if.end59 unwind label %lpad29

if.end59:                                         ; preds = %if.else.i.i, %_ZSt12construct_atINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEJS5_EEDTgsnwcvPvLi0E_T_pispclsr3stdE7declvalIT0_EEEEPS7_DpOS8_.exit.i.i, %for.cond.cleanup38
  %73 = load ptr, ptr %normalized, align 8, !tbaa !13
  %cmp.i.i.i263 = icmp eq ptr %73, %49
  br i1 %cmp.i.i.i263, label %if.then.i.i.i266, label %if.then.i.i264

if.then.i.i.i266:                                 ; preds = %if.end59
  %74 = load i64, ptr %_M_string_length.i.i.i245, align 8, !tbaa !16
  %cmp3.i.i.i268 = icmp ult i64 %74, 16
  call void @llvm.assume(i1 %cmp3.i.i.i268)
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit269

if.then.i.i264:                                   ; preds = %if.end59
  %75 = load i64, ptr %49, align 8, !tbaa !15
  %add.i.i.i265 = add i64 %75, 1
  call void @_ZdlPvm(ptr noundef %73, i64 noundef %add.i.i.i265) #23
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit269

_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit269: ; preds = %if.then.i.i264, %if.then.i.i.i266
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %normalized) #20
  %incdec.ptr.i270 = getelementptr inbounds nuw i8, ptr %__begin2.sroa.0.0387, i64 32
  %cmp.i236 = icmp eq ptr %incdec.ptr.i270, %48
  br i1 %cmp.i236, label %for.cond.cleanup25, label %for.body26, !llvm.loop !51

ehcleanup60:                                      ; preds = %lpad41, %lpad29
  %.pn215 = phi { ptr, i32 } [ %67, %lpad41 ], [ %60, %lpad29 ]
  %76 = load ptr, ptr %normalized, align 8, !tbaa !13
  %cmp.i.i.i271 = icmp eq ptr %76, %49
  br i1 %cmp.i.i.i271, label %if.then.i.i.i274, label %if.then.i.i272

if.then.i.i.i274:                                 ; preds = %ehcleanup60
  %77 = load i64, ptr %_M_string_length.i.i.i245, align 8, !tbaa !16
  %cmp3.i.i.i276 = icmp ult i64 %77, 16
  call void @llvm.assume(i1 %cmp3.i.i.i276)
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit277

if.then.i.i272:                                   ; preds = %ehcleanup60
  %78 = load i64, ptr %49, align 8, !tbaa !15
  %add.i.i.i273 = add i64 %78, 1
  call void @_ZdlPvm(ptr noundef %76, i64 noundef %add.i.i.i273) #23
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit277

_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit277: ; preds = %if.then.i.i272, %if.then.i.i.i274
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %normalized) #20
  br label %ehcleanup172

invoke.cont70:                                    ; preds = %for.cond.cleanup25
  %79 = load ptr, ptr %agg.tmp, align 8, !tbaa !13
  %cmp.i.i.i278 = icmp eq ptr %79, %50
  br i1 %cmp.i.i.i278, label %if.then.i.i.i281, label %if.then.i.i279

if.then.i.i.i281:                                 ; preds = %invoke.cont70
  %80 = load i64, ptr %_M_string_length.i.i.i237, align 8, !tbaa !16
  %cmp3.i.i.i283 = icmp ult i64 %80, 16
  call void @llvm.assume(i1 %cmp3.i.i.i283)
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit284

if.then.i.i279:                                   ; preds = %invoke.cont70
  %81 = load i64, ptr %50, align 8, !tbaa !15
  %add.i.i.i280 = add i64 %81, 1
  call void @_ZdlPvm(ptr noundef %79, i64 noundef %add.i.i.i280) #23
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit284

_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit284: ; preds = %if.then.i.i279, %if.then.i.i.i281
  call void @llvm.lifetime.start.p0(i64 24, ptr nonnull %frequency_items) #20
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 8 dereferenceable(24) %frequency_items, i8 0, i64 24, i1 false)
  %_M_element_count.i.i = getelementptr inbounds nuw i8, ptr %frequencies, i64 24
  %82 = load i64, ptr %_M_element_count.i.i, align 8, !tbaa !52
  invoke void @_ZNSt6vectorISt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmESaIS7_EE7reserveEm(ptr noundef nonnull align 8 dereferenceable(24) %frequency_items, i64 noundef %82)
          to label %invoke.cont74 unwind label %lpad73

invoke.cont74:                                    ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit284
  %83 = load ptr, ptr %_M_before_begin.i.i, align 8, !tbaa !53
  %cmp.i.i285388 = icmp eq ptr %83, null
  br i1 %cmp.i.i285388, label %for.cond.cleanup87, label %for.body88

for.cond.cleanup87:                               ; preds = %invoke.cont94, %invoke.cont74
  %_M_finish.i286 = getelementptr inbounds nuw i8, ptr %frequency_items, i64 8
  %84 = load ptr, ptr %_M_finish.i286, align 8, !tbaa !54
  %85 = load ptr, ptr %frequency_items, align 8, !tbaa !57
  %sub.ptr.lhs.cast.i = ptrtoint ptr %84 to i64
  %sub.ptr.rhs.cast.i = ptrtoint ptr %85 to i64
  %sub.ptr.sub.i = sub i64 %sub.ptr.lhs.cast.i, %sub.ptr.rhs.cast.i
  %sub.ptr.div.i = sdiv exact i64 %sub.ptr.sub.i, 40
  %.sroa.speculated = call i64 @llvm.umin.i64(i64 %max_results, i64 %sub.ptr.div.i)
  %cmp111 = icmp eq i64 %.sroa.speculated, 0
  br i1 %cmp111, label %cleanup161, label %if.end113

lpad69:                                           ; preds = %for.cond.cleanup25
  %86 = landingpad { ptr, i32 }
          catch ptr null
  %87 = load ptr, ptr %agg.tmp, align 8, !tbaa !13
  %cmp.i.i.i288 = icmp eq ptr %87, %50
  br i1 %cmp.i.i.i288, label %if.then.i.i.i291, label %if.then.i.i289

if.then.i.i.i291:                                 ; preds = %lpad69
  %88 = load i64, ptr %_M_string_length.i.i.i237, align 8, !tbaa !16
  %cmp3.i.i.i293 = icmp ult i64 %88, 16
  call void @llvm.assume(i1 %cmp3.i.i.i293)
  br label %ehcleanup168

if.then.i.i289:                                   ; preds = %lpad69
  %89 = load i64, ptr %50, align 8, !tbaa !15
  %add.i.i.i290 = add i64 %89, 1
  call void @_ZdlPvm(ptr noundef %87, i64 noundef %add.i.i.i290) #23
  br label %ehcleanup168

lpad73:                                           ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit284
  %90 = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup164

for.body88:                                       ; preds = %invoke.cont94, %invoke.cont74
  %__begin276.sroa.0.0389 = phi ptr [ %91, %invoke.cont94 ], [ %83, %invoke.cont74 ]
  %add.ptr.i295 = getelementptr inbounds nuw i8, ptr %__begin276.sroa.0.0389, i64 8
  %second.i.i = getelementptr inbounds nuw i8, ptr %__begin276.sroa.0.0389, i64 40
  %call95 = invoke noundef nonnull align 8 dereferenceable(40) ptr @_ZNSt6vectorISt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmESaIS7_EE12emplace_backIJRKS6_RKmEEERS7_DpOT_(ptr noundef nonnull align 8 dereferenceable(24) %frequency_items, ptr noundef nonnull align 8 dereferenceable(32) %add.ptr.i295, ptr noundef nonnull align 8 dereferenceable(8) %second.i.i)
          to label %invoke.cont94 unwind label %lpad93

invoke.cont94:                                    ; preds = %for.body88
  %91 = load ptr, ptr %__begin276.sroa.0.0389, align 8, !tbaa !58
  %cmp.i.i285 = icmp eq ptr %91, null
  br i1 %cmp.i.i285, label %for.cond.cleanup87, label %for.body88, !llvm.loop !59

lpad93:                                           ; preds = %for.body88
  %92 = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup164

if.end113:                                        ; preds = %for.cond.cleanup87
  %call114 = call noalias ptr @calloc(i64 noundef %.sroa.speculated, i64 noundef 16) #24
  %cmp115 = icmp eq ptr %call114, null
  br i1 %cmp115, label %cleanup161, label %if.end117

if.end117:                                        ; preds = %if.end113
  call void @llvm.lifetime.start.p0(i64 16, ptr nonnull %result_guard) #20
  store i64 %.sroa.speculated, ptr %result_guard, align 8, !tbaa !4
  %93 = getelementptr inbounds nuw i8, ptr %result_guard, i64 8
  store ptr %call114, ptr %93, align 8, !tbaa !60
  %sub.i = add i64 %.sroa.speculated, -1
  %arrayidx8.i = getelementptr inbounds nuw %struct.WordCount, ptr %call114, i64 %sub.i
  br label %for.body122

for.cond.cleanup121:                              ; preds = %for.inc126
  %94 = load ptr, ptr %frequency_items, align 8, !tbaa !63
  %add.ptr.i296 = getelementptr inbounds %"struct.std::pair.14", ptr %94, i64 %.sroa.speculated
  %95 = load ptr, ptr %_M_finish.i286, align 8, !tbaa !63
  invoke fastcc void @_ZL23find_top_tail_recursiveN9__gnu_cxx17__normal_iteratorIPKSt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmESt6vectorIS8_SaIS8_EEEESE_P9WordCountm(ptr nonnull %add.ptr.i296, ptr %95, ptr noundef %call114, i64 noundef %.sroa.speculated)
          to label %invoke.cont145 unwind label %lpad144

for.body122:                                      ; preds = %for.inc126, %if.end117
  %i118.0390 = phi i64 [ 0, %if.end117 ], [ %inc127, %for.inc126 ]
  %96 = load ptr, ptr %frequency_items, align 8, !tbaa !57
  %add.ptr.i298 = getelementptr inbounds nuw %"struct.std::pair.14", ptr %96, i64 %i118.0390
  %call.i309 = invoke noundef ptr @_Z16copy_to_c_stringRKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE(ptr noundef nonnull align 8 dereferenceable(40) %add.ptr.i298)
          to label %call.i.noexc unwind label %lpad124.loopexit

call.i.noexc:                                     ; preds = %for.body122
  %cmp.i299 = icmp eq ptr %call.i309, null
  br i1 %cmp.i299, label %if.then.i307, label %if.end.i300

if.then.i307:                                     ; preds = %call.i.noexc
  %exception.i308 = call ptr @__cxa_allocate_exception(i64 8) #20
  store ptr getelementptr inbounds nuw inrange(-16, 24) (i8, ptr @_ZTVSt9bad_alloc, i64 16), ptr %exception.i308, align 8, !tbaa !28
  invoke void @__cxa_throw(ptr nonnull %exception.i308, ptr nonnull @_ZTISt9bad_alloc, ptr nonnull @_ZNSt9bad_allocD1Ev) #21
          to label %.noexc310 unwind label %lpad124.loopexit.split-lp

.noexc310:                                        ; preds = %if.then.i307
  unreachable

if.end.i300:                                      ; preds = %call.i.noexc
  %second.i = getelementptr inbounds nuw i8, ptr %add.ptr.i298, i64 32
  %97 = load i64, ptr %second.i, align 8, !tbaa !64
  br label %for.body.i

for.body.i:                                       ; preds = %for.inc.i, %if.end.i300
  %i.044.i = phi i64 [ 0, %if.end.i300 ], [ %inc.i, %for.inc.i ]
  %arrayidx.i301 = getelementptr inbounds nuw %struct.WordCount, ptr %call114, i64 %i.044.i
  %count1.i.i = getelementptr inbounds nuw i8, ptr %arrayidx.i301, i64 8
  %98 = load i64, ptr %count1.i.i, align 8, !tbaa !66
  %cmp.not.i.i302 = icmp eq i64 %97, %98
  br i1 %cmp.not.i.i302, label %if.end.i.i305, label %if.then.i.i303

if.then.i.i303:                                   ; preds = %for.body.i
  %cmp4.i.i = icmp ugt i64 %97, %98
  br label %_ZL19is_better_candidateRK9WordCountS1_.exit.i

if.end.i.i305:                                    ; preds = %for.body.i
  %99 = load ptr, ptr %arrayidx.i301, align 8, !tbaa !68
  %call.i.i306 = call i32 @strcmp(ptr noundef nonnull dereferenceable(1) %call.i309, ptr noundef nonnull dereferenceable(1) %99) #25
  %cmp6.i.i = icmp slt i32 %call.i.i306, 0
  br label %_ZL19is_better_candidateRK9WordCountS1_.exit.i

_ZL19is_better_candidateRK9WordCountS1_.exit.i:   ; preds = %if.end.i.i305, %if.then.i.i303
  %retval.0.i.i = phi i1 [ %cmp4.i.i, %if.then.i.i303 ], [ %cmp6.i.i, %if.end.i.i305 ]
  br i1 %retval.0.i.i, label %cleanup.i, label %for.inc.i

for.inc.i:                                        ; preds = %_ZL19is_better_candidateRK9WordCountS1_.exit.i
  %inc.i = add nuw i64 %i.044.i, 1
  %exitcond.not.i = icmp eq i64 %inc.i, %.sroa.speculated
  br i1 %exitcond.not.i, label %cleanup.i, label %for.body.i, !llvm.loop !69

cleanup.i:                                        ; preds = %for.inc.i, %_ZL19is_better_candidateRK9WordCountS1_.exit.i
  %insert_pos.0.i = phi i64 [ %.sroa.speculated, %for.inc.i ], [ %i.044.i, %_ZL19is_better_candidateRK9WordCountS1_.exit.i ]
  %cmp6.i = icmp ult i64 %insert_pos.0.i, %.sroa.speculated
  br i1 %cmp6.i, label %if.then7.i, label %if.else.i304

if.then7.i:                                       ; preds = %cleanup.i
  %100 = load ptr, ptr %arrayidx8.i, align 8, !tbaa !68
  call void @free(ptr noundef %100) #20
  %cmp1345.i = icmp ugt i64 %sub.i, %insert_pos.0.i
  br i1 %cmp1345.i, label %for.body15.i, label %for.cond.cleanup14.i

for.cond.cleanup14.i:                             ; preds = %for.body15.i, %if.then7.i
  %arrayidx22.i = getelementptr inbounds nuw %struct.WordCount, ptr %call114, i64 %insert_pos.0.i
  store ptr %call.i309, ptr %arrayidx22.i, align 8, !tbaa !20
  %new_entry.sroa.6.0.arrayidx22.sroa_idx.i = getelementptr inbounds nuw i8, ptr %arrayidx22.i, i64 8
  store i64 %97, ptr %new_entry.sroa.6.0.arrayidx22.sroa_idx.i, align 8, !tbaa !4
  br label %for.inc126

for.body15.i:                                     ; preds = %for.body15.i, %if.then7.i
  %i10.046.i = phi i64 [ %dec.i, %for.body15.i ], [ %sub.i, %if.then7.i ]
  %101 = getelementptr %struct.WordCount, ptr %call114, i64 %i10.046.i
  %arrayidx17.i = getelementptr i8, ptr %101, i64 -16
  call void @llvm.memcpy.p0.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %101, ptr noundef nonnull align 8 dereferenceable(16) %arrayidx17.i, i64 16, i1 false), !tbaa.struct !70
  %dec.i = add i64 %i10.046.i, -1
  %cmp13.i = icmp ugt i64 %dec.i, %insert_pos.0.i
  br i1 %cmp13.i, label %for.body15.i, label %for.cond.cleanup14.i, !llvm.loop !71

if.else.i304:                                     ; preds = %cleanup.i
  call void @free(ptr noundef %call.i309) #20
  br label %for.inc126

for.inc126:                                       ; preds = %if.else.i304, %for.cond.cleanup14.i
  %inc127 = add nuw i64 %i118.0390, 1
  %exitcond393.not = icmp eq i64 %inc127, %.sroa.speculated
  br i1 %exitcond393.not, label %for.cond.cleanup121, label %for.body122, !llvm.loop !72

lpad124.loopexit:                                 ; preds = %for.body122
  %lpad.loopexit = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup154

lpad124.loopexit.split-lp:                        ; preds = %if.then.i307
  %lpad.loopexit.split-lp = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup154

invoke.cont145:                                   ; preds = %for.cond.cleanup121
  br i1 %cmp.not, label %if.end151, label %if.then150

if.then150:                                       ; preds = %invoke.cont145
  store i64 %.sroa.speculated, ptr %result_length, align 8, !tbaa !4
  br label %if.end151

lpad144:                                          ; preds = %for.cond.cleanup121
  %102 = landingpad { ptr, i32 }
          catch ptr null
  br label %ehcleanup154

if.end151:                                        ; preds = %if.then150, %invoke.cont145
  store ptr null, ptr %93, align 8, !tbaa !73
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %result_guard) #20
  br label %cleanup161

ehcleanup154:                                     ; preds = %lpad144, %lpad124.loopexit.split-lp, %lpad124.loopexit
  %.pn213 = phi { ptr, i32 } [ %102, %lpad144 ], [ %lpad.loopexit, %lpad124.loopexit ], [ %lpad.loopexit.split-lp, %lpad124.loopexit.split-lp ]
  call fastcc void @"_ZNSt10unique_ptrI9WordCountKZ19top_words_from_fileE3$_0ED2Ev"(ptr noundef nonnull align 8 dereferenceable(16) %result_guard) #20
  call void @llvm.lifetime.end.p0(i64 16, ptr nonnull %result_guard) #20
  br label %ehcleanup164

cleanup161:                                       ; preds = %if.end151, %if.end113, %for.cond.cleanup87
  %retval.1 = phi ptr [ null, %for.cond.cleanup87 ], [ %call114, %if.end151 ], [ null, %if.end113 ]
  %103 = load ptr, ptr %frequency_items, align 8, !tbaa !57
  %104 = load ptr, ptr %_M_finish.i286, align 8, !tbaa !54
  %cmp.not3.i.i.i = icmp eq ptr %103, %104
  br i1 %cmp.not3.i.i.i, label %invoke.cont.i, label %for.body.i.i.i

for.body.i.i.i:                                   ; preds = %_ZSt8_DestroyISt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmEEvPT_.exit.i.i.i, %cleanup161
  %__first.addr.04.i.i.i = phi ptr [ %incdec.ptr.i.i.i, %_ZSt8_DestroyISt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmEEvPT_.exit.i.i.i ], [ %103, %cleanup161 ]
  %105 = load ptr, ptr %__first.addr.04.i.i.i, align 8, !tbaa !13
  %106 = getelementptr inbounds nuw i8, ptr %__first.addr.04.i.i.i, i64 16
  %cmp.i.i.i.i.i.i.i.i.i = icmp eq ptr %105, %106
  br i1 %cmp.i.i.i.i.i.i.i.i.i, label %if.then.i.i.i.i.i.i.i.i.i, label %if.then.i.i.i.i.i.i.i.i

if.then.i.i.i.i.i.i.i.i.i:                        ; preds = %for.body.i.i.i
  %_M_string_length.i.i.i.i.i.i.i.i.i = getelementptr inbounds nuw i8, ptr %__first.addr.04.i.i.i, i64 8
  %107 = load i64, ptr %_M_string_length.i.i.i.i.i.i.i.i.i, align 8, !tbaa !16
  %cmp3.i.i.i.i.i.i.i.i.i = icmp ult i64 %107, 16
  call void @llvm.assume(i1 %cmp3.i.i.i.i.i.i.i.i.i)
  br label %_ZSt8_DestroyISt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmEEvPT_.exit.i.i.i

if.then.i.i.i.i.i.i.i.i:                          ; preds = %for.body.i.i.i
  %108 = load i64, ptr %106, align 8, !tbaa !15
  %add.i.i.i.i.i.i.i.i.i = add i64 %108, 1
  call void @_ZdlPvm(ptr noundef %105, i64 noundef %add.i.i.i.i.i.i.i.i.i) #23
  br label %_ZSt8_DestroyISt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmEEvPT_.exit.i.i.i

_ZSt8_DestroyISt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmEEvPT_.exit.i.i.i: ; preds = %if.then.i.i.i.i.i.i.i.i, %if.then.i.i.i.i.i.i.i.i.i
  %incdec.ptr.i.i.i = getelementptr inbounds nuw i8, ptr %__first.addr.04.i.i.i, i64 40
  %cmp.not.i.i.i = icmp eq ptr %incdec.ptr.i.i.i, %104
  br i1 %cmp.not.i.i.i, label %invoke.cont.i, label %for.body.i.i.i, !llvm.loop !74

invoke.cont.i:                                    ; preds = %_ZSt8_DestroyISt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmEEvPT_.exit.i.i.i, %cleanup161
  %109 = load ptr, ptr %frequency_items, align 8, !tbaa !57
  %tobool.not.i.i.i = icmp eq ptr %109, null
  br i1 %tobool.not.i.i.i, label %_ZNSt6vectorISt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmESaIS7_EED2Ev.exit, label %if.then.i.i.i315

if.then.i.i.i315:                                 ; preds = %invoke.cont.i
  %_M_end_of_storage.i.i316 = getelementptr inbounds nuw i8, ptr %frequency_items, i64 16
  %110 = load ptr, ptr %_M_end_of_storage.i.i316, align 8, !tbaa !75
  %sub.ptr.lhs.cast.i.i = ptrtoint ptr %110 to i64
  %sub.ptr.rhs.cast.i.i = ptrtoint ptr %109 to i64
  %sub.ptr.sub.i.i = sub i64 %sub.ptr.lhs.cast.i.i, %sub.ptr.rhs.cast.i.i
  call void @_ZdlPvm(ptr noundef nonnull %109, i64 noundef %sub.ptr.sub.i.i) #23
  br label %_ZNSt6vectorISt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmESaIS7_EED2Ev.exit

_ZNSt6vectorISt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmESaIS7_EED2Ev.exit: ; preds = %if.then.i.i.i315, %invoke.cont.i
  call void @llvm.lifetime.end.p0(i64 24, ptr nonnull %frequency_items) #20
  %111 = load ptr, ptr %_M_before_begin.i.i, align 8, !tbaa !53
  %tobool.not4.i.i.i.i = icmp eq ptr %111, null
  br i1 %tobool.not4.i.i.i.i, label %_ZNSt10_HashtableINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESt4pairIKS5_mESaIS8_ENSt8__detail10_Select1stESt8equal_toIS5_ESt4hashIS5_ENSA_18_Mod_range_hashingENSA_20_Default_ranged_hashENSA_20_Prime_rehash_policyENSA_17_Hashtable_traitsILb1ELb0ELb1EEEE5clearEv.exit.i.i, label %while.body.i.i.i.i

while.body.i.i.i.i:                               ; preds = %_ZNSt8__detail16_Hashtable_allocISaINS_10_Hash_nodeISt4pairIKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmELb1EEEEE18_M_deallocate_nodeEPSB_.exit.i.i.i.i, %_ZNSt6vectorISt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmESaIS7_EED2Ev.exit
  %__n.addr.05.i.i.i.i = phi ptr [ %112, %_ZNSt8__detail16_Hashtable_allocISaINS_10_Hash_nodeISt4pairIKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmELb1EEEEE18_M_deallocate_nodeEPSB_.exit.i.i.i.i ], [ %111, %_ZNSt6vectorISt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmESaIS7_EED2Ev.exit ]
  %112 = load ptr, ptr %__n.addr.05.i.i.i.i, align 8, !tbaa !58
  %add.ptr.i.i.i.i.i317 = getelementptr inbounds nuw i8, ptr %__n.addr.05.i.i.i.i, i64 8
  %113 = load ptr, ptr %add.ptr.i.i.i.i.i317, align 8, !tbaa !13
  %114 = getelementptr inbounds nuw i8, ptr %__n.addr.05.i.i.i.i, i64 24
  %cmp.i.i.i.i.i.i.i.i.i.i = icmp eq ptr %113, %114
  br i1 %cmp.i.i.i.i.i.i.i.i.i.i, label %if.then.i.i.i.i.i.i.i.i.i.i, label %if.then.i.i.i.i.i.i.i.i.i318

if.then.i.i.i.i.i.i.i.i.i.i:                      ; preds = %while.body.i.i.i.i
  %_M_string_length.i.i.i.i.i.i.i.i.i.i = getelementptr inbounds nuw i8, ptr %__n.addr.05.i.i.i.i, i64 16
  %115 = load i64, ptr %_M_string_length.i.i.i.i.i.i.i.i.i.i, align 8, !tbaa !16
  %cmp3.i.i.i.i.i.i.i.i.i.i = icmp ult i64 %115, 16
  call void @llvm.assume(i1 %cmp3.i.i.i.i.i.i.i.i.i.i)
  br label %_ZNSt8__detail16_Hashtable_allocISaINS_10_Hash_nodeISt4pairIKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmELb1EEEEE18_M_deallocate_nodeEPSB_.exit.i.i.i.i

if.then.i.i.i.i.i.i.i.i.i318:                     ; preds = %while.body.i.i.i.i
  %116 = load i64, ptr %114, align 8, !tbaa !15
  %add.i.i.i.i.i.i.i.i.i.i = add i64 %116, 1
  call void @_ZdlPvm(ptr noundef %113, i64 noundef %add.i.i.i.i.i.i.i.i.i.i) #23
  br label %_ZNSt8__detail16_Hashtable_allocISaINS_10_Hash_nodeISt4pairIKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmELb1EEEEE18_M_deallocate_nodeEPSB_.exit.i.i.i.i

_ZNSt8__detail16_Hashtable_allocISaINS_10_Hash_nodeISt4pairIKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmELb1EEEEE18_M_deallocate_nodeEPSB_.exit.i.i.i.i: ; preds = %if.then.i.i.i.i.i.i.i.i.i318, %if.then.i.i.i.i.i.i.i.i.i.i
  call void @_ZdlPvm(ptr noundef nonnull %__n.addr.05.i.i.i.i, i64 noundef 56) #23
  %tobool.not.i.i.i.i = icmp eq ptr %112, null
  br i1 %tobool.not.i.i.i.i, label %_ZNSt10_HashtableINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESt4pairIKS5_mESaIS8_ENSt8__detail10_Select1stESt8equal_toIS5_ESt4hashIS5_ENSA_18_Mod_range_hashingENSA_20_Default_ranged_hashENSA_20_Prime_rehash_policyENSA_17_Hashtable_traitsILb1ELb0ELb1EEEE5clearEv.exit.i.i, label %while.body.i.i.i.i, !llvm.loop !76

_ZNSt10_HashtableINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESt4pairIKS5_mESaIS8_ENSt8__detail10_Select1stESt8equal_toIS5_ESt4hashIS5_ENSA_18_Mod_range_hashingENSA_20_Default_ranged_hashENSA_20_Prime_rehash_policyENSA_17_Hashtable_traitsILb1ELb0ELb1EEEE5clearEv.exit.i.i: ; preds = %_ZNSt8__detail16_Hashtable_allocISaINS_10_Hash_nodeISt4pairIKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmELb1EEEEE18_M_deallocate_nodeEPSB_.exit.i.i.i.i, %_ZNSt6vectorISt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmESaIS7_EED2Ev.exit
  %117 = load ptr, ptr %frequencies, align 8, !tbaa !41
  %118 = load i64, ptr %_M_bucket_count.i.i, align 8, !tbaa !48
  %mul.i.i.i = shl i64 %118, 3
  call void @llvm.memset.p0.i64(ptr align 8 %117, i8 0, i64 %mul.i.i.i, i1 false)
  call void @llvm.memset.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %_M_before_begin.i.i, i8 0, i64 16, i1 false)
  %119 = load ptr, ptr %frequencies, align 8, !tbaa !41
  %cmp.i.i.i.i.i319 = icmp eq ptr %119, %_M_single_bucket.i.i
  br i1 %cmp.i.i.i.i.i319, label %_ZNSt13unordered_mapINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmSt4hashIS5_ESt8equal_toIS5_ESaISt4pairIKS5_mEEED2Ev.exit, label %if.end.i.i.i.i

if.end.i.i.i.i:                                   ; preds = %_ZNSt10_HashtableINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESt4pairIKS5_mESaIS8_ENSt8__detail10_Select1stESt8equal_toIS5_ESt4hashIS5_ENSA_18_Mod_range_hashingENSA_20_Default_ranged_hashENSA_20_Prime_rehash_policyENSA_17_Hashtable_traitsILb1ELb0ELb1EEEE5clearEv.exit.i.i
  %120 = load i64, ptr %_M_bucket_count.i.i, align 8, !tbaa !48
  %mul.i.i.i.i.i.i = shl i64 %120, 3
  call void @_ZdlPvm(ptr noundef %119, i64 noundef %mul.i.i.i.i.i.i) #23
  br label %_ZNSt13unordered_mapINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmSt4hashIS5_ESt8equal_toIS5_ESaISt4pairIKS5_mEEED2Ev.exit

_ZNSt13unordered_mapINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmSt4hashIS5_ESt8equal_toIS5_ESaISt4pairIKS5_mEEED2Ev.exit: ; preds = %if.end.i.i.i.i, %_ZNSt10_HashtableINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESt4pairIKS5_mESaIS8_ENSt8__detail10_Select1stESt8equal_toIS5_ESt4hashIS5_ENSA_18_Mod_range_hashingENSA_20_Default_ranged_hashENSA_20_Prime_rehash_policyENSA_17_Hashtable_traitsILb1ELb0ELb1EEEE5clearEv.exit.i.i
  call void @llvm.lifetime.end.p0(i64 56, ptr nonnull %frequencies) #20
  %121 = load ptr, ptr %normalized_ignore, align 8, !tbaa !77
  %_M_finish.i320 = getelementptr inbounds nuw i8, ptr %normalized_ignore, i64 8
  %122 = load ptr, ptr %_M_finish.i320, align 8, !tbaa !21
  %cmp.not3.i.i.i321 = icmp eq ptr %121, %122
  br i1 %cmp.not3.i.i.i321, label %invoke.cont.i326, label %for.body.i.i.i322

for.body.i.i.i322:                                ; preds = %_ZSt8_DestroyINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEEvPT_.exit.i.i.i, %_ZNSt13unordered_mapINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmSt4hashIS5_ESt8equal_toIS5_ESaISt4pairIKS5_mEEED2Ev.exit
  %__first.addr.04.i.i.i323 = phi ptr [ %incdec.ptr.i.i.i324, %_ZSt8_DestroyINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEEvPT_.exit.i.i.i ], [ %121, %_ZNSt13unordered_mapINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmSt4hashIS5_ESt8equal_toIS5_ESaISt4pairIKS5_mEEED2Ev.exit ]
  %123 = load ptr, ptr %__first.addr.04.i.i.i323, align 8, !tbaa !13
  %124 = getelementptr inbounds nuw i8, ptr %__first.addr.04.i.i.i323, i64 16
  %cmp.i.i.i.i.i.i.i.i = icmp eq ptr %123, %124
  br i1 %cmp.i.i.i.i.i.i.i.i, label %if.then.i.i.i.i.i.i.i.i333, label %if.then.i.i.i.i.i.i.i

if.then.i.i.i.i.i.i.i.i333:                       ; preds = %for.body.i.i.i322
  %_M_string_length.i.i.i.i.i.i.i.i = getelementptr inbounds nuw i8, ptr %__first.addr.04.i.i.i323, i64 8
  %125 = load i64, ptr %_M_string_length.i.i.i.i.i.i.i.i, align 8, !tbaa !16
  %cmp3.i.i.i.i.i.i.i.i = icmp ult i64 %125, 16
  call void @llvm.assume(i1 %cmp3.i.i.i.i.i.i.i.i)
  br label %_ZSt8_DestroyINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEEvPT_.exit.i.i.i

if.then.i.i.i.i.i.i.i:                            ; preds = %for.body.i.i.i322
  %126 = load i64, ptr %124, align 8, !tbaa !15
  %add.i.i.i.i.i.i.i.i = add i64 %126, 1
  call void @_ZdlPvm(ptr noundef %123, i64 noundef %add.i.i.i.i.i.i.i.i) #23
  br label %_ZSt8_DestroyINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEEvPT_.exit.i.i.i

_ZSt8_DestroyINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEEvPT_.exit.i.i.i: ; preds = %if.then.i.i.i.i.i.i.i, %if.then.i.i.i.i.i.i.i.i333
  %incdec.ptr.i.i.i324 = getelementptr inbounds nuw i8, ptr %__first.addr.04.i.i.i323, i64 32
  %cmp.not.i.i.i325 = icmp eq ptr %incdec.ptr.i.i.i324, %122
  br i1 %cmp.not.i.i.i325, label %invoke.cont.i326, label %for.body.i.i.i322, !llvm.loop !78

invoke.cont.i326:                                 ; preds = %_ZSt8_DestroyINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEEvPT_.exit.i.i.i, %_ZNSt13unordered_mapINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmSt4hashIS5_ESt8equal_toIS5_ESaISt4pairIKS5_mEEED2Ev.exit
  %127 = load ptr, ptr %normalized_ignore, align 8, !tbaa !77
  %tobool.not.i.i.i327 = icmp eq ptr %127, null
  br i1 %tobool.not.i.i.i327, label %_ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EED2Ev.exit, label %if.then.i.i.i328

if.then.i.i.i328:                                 ; preds = %invoke.cont.i326
  %_M_end_of_storage.i.i329 = getelementptr inbounds nuw i8, ptr %normalized_ignore, i64 16
  %128 = load ptr, ptr %_M_end_of_storage.i.i329, align 8, !tbaa !24
  %sub.ptr.lhs.cast.i.i330 = ptrtoint ptr %128 to i64
  %sub.ptr.rhs.cast.i.i331 = ptrtoint ptr %127 to i64
  %sub.ptr.sub.i.i332 = sub i64 %sub.ptr.lhs.cast.i.i330, %sub.ptr.rhs.cast.i.i331
  call void @_ZdlPvm(ptr noundef nonnull %127, i64 noundef %sub.ptr.sub.i.i332) #23
  br label %_ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EED2Ev.exit

_ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EED2Ev.exit: ; preds = %if.then.i.i.i328, %invoke.cont.i326
  call void @llvm.lifetime.end.p0(i64 24, ptr nonnull %normalized_ignore) #20
  %129 = load ptr, ptr %text, align 8, !tbaa !13
  %cmp.i.i.i334 = icmp eq ptr %129, %26
  br i1 %cmp.i.i.i334, label %if.then.i.i.i338, label %if.then.i.i335

if.then.i.i.i338:                                 ; preds = %_ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EED2Ev.exit
  %130 = load i64, ptr %_M_string_length.i.i.i88.i, align 8, !tbaa !16
  %cmp3.i.i.i340 = icmp ult i64 %130, 16
  call void @llvm.assume(i1 %cmp3.i.i.i340)
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit341

if.then.i.i335:                                   ; preds = %_ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EED2Ev.exit
  %131 = load i64, ptr %26, align 8, !tbaa !15
  %add.i.i.i336 = add i64 %131, 1
  call void @_ZdlPvm(ptr noundef %129, i64 noundef %add.i.i.i336) #23
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit341

_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit341: ; preds = %if.then.i.i335, %if.then.i.i.i338
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %text) #20
  %132 = load ptr, ptr %ignore, align 8, !tbaa !77
  %133 = load ptr, ptr %_M_finish.i235, align 8, !tbaa !21
  %cmp.not3.i.i.i343 = icmp eq ptr %132, %133
  br i1 %cmp.not3.i.i.i343, label %invoke.cont.i352, label %for.body.i.i.i344

for.body.i.i.i344:                                ; preds = %_ZSt8_DestroyINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEEvPT_.exit.i.i.i349, %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit341
  %__first.addr.04.i.i.i345 = phi ptr [ %incdec.ptr.i.i.i350, %_ZSt8_DestroyINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEEvPT_.exit.i.i.i349 ], [ %132, %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit341 ]
  %134 = load ptr, ptr %__first.addr.04.i.i.i345, align 8, !tbaa !13
  %135 = getelementptr inbounds nuw i8, ptr %__first.addr.04.i.i.i345, i64 16
  %cmp.i.i.i.i.i.i.i.i346 = icmp eq ptr %134, %135
  br i1 %cmp.i.i.i.i.i.i.i.i346, label %if.then.i.i.i.i.i.i.i.i359, label %if.then.i.i.i.i.i.i.i347

if.then.i.i.i.i.i.i.i.i359:                       ; preds = %for.body.i.i.i344
  %_M_string_length.i.i.i.i.i.i.i.i360 = getelementptr inbounds nuw i8, ptr %__first.addr.04.i.i.i345, i64 8
  %136 = load i64, ptr %_M_string_length.i.i.i.i.i.i.i.i360, align 8, !tbaa !16
  %cmp3.i.i.i.i.i.i.i.i361 = icmp ult i64 %136, 16
  call void @llvm.assume(i1 %cmp3.i.i.i.i.i.i.i.i361)
  br label %_ZSt8_DestroyINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEEvPT_.exit.i.i.i349

if.then.i.i.i.i.i.i.i347:                         ; preds = %for.body.i.i.i344
  %137 = load i64, ptr %135, align 8, !tbaa !15
  %add.i.i.i.i.i.i.i.i348 = add i64 %137, 1
  call void @_ZdlPvm(ptr noundef %134, i64 noundef %add.i.i.i.i.i.i.i.i348) #23
  br label %_ZSt8_DestroyINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEEvPT_.exit.i.i.i349

_ZSt8_DestroyINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEEvPT_.exit.i.i.i349: ; preds = %if.then.i.i.i.i.i.i.i347, %if.then.i.i.i.i.i.i.i.i359
  %incdec.ptr.i.i.i350 = getelementptr inbounds nuw i8, ptr %__first.addr.04.i.i.i345, i64 32
  %cmp.not.i.i.i351 = icmp eq ptr %incdec.ptr.i.i.i350, %133
  br i1 %cmp.not.i.i.i351, label %invoke.cont.i352, label %for.body.i.i.i344, !llvm.loop !78

invoke.cont.i352:                                 ; preds = %_ZSt8_DestroyINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEEvPT_.exit.i.i.i349, %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit341
  %138 = load ptr, ptr %ignore, align 8, !tbaa !77
  %tobool.not.i.i.i353 = icmp eq ptr %138, null
  br i1 %tobool.not.i.i.i353, label %_ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EED2Ev.exit362, label %if.then.i.i.i354

if.then.i.i.i354:                                 ; preds = %invoke.cont.i352
  %_M_end_of_storage.i.i355 = getelementptr inbounds nuw i8, ptr %ignore, i64 16
  %139 = load ptr, ptr %_M_end_of_storage.i.i355, align 8, !tbaa !24
  %sub.ptr.lhs.cast.i.i356 = ptrtoint ptr %139 to i64
  %sub.ptr.rhs.cast.i.i357 = ptrtoint ptr %138 to i64
  %sub.ptr.sub.i.i358 = sub i64 %sub.ptr.lhs.cast.i.i356, %sub.ptr.rhs.cast.i.i357
  call void @_ZdlPvm(ptr noundef nonnull %138, i64 noundef %sub.ptr.sub.i.i358) #23
  br label %_ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EED2Ev.exit362

_ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EED2Ev.exit362: ; preds = %if.then.i.i.i354, %invoke.cont.i352
  call void @llvm.lifetime.end.p0(i64 24, ptr nonnull %ignore) #20
  br label %return

ehcleanup164:                                     ; preds = %ehcleanup154, %lpad93, %lpad73
  %.pn214 = phi { ptr, i32 } [ %92, %lpad93 ], [ %.pn213, %ehcleanup154 ], [ %90, %lpad73 ]
  call void @_ZNSt6vectorISt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmESaIS7_EED2Ev(ptr noundef nonnull align 8 dereferenceable(24) %frequency_items) #20
  call void @llvm.lifetime.end.p0(i64 24, ptr nonnull %frequency_items) #20
  br label %ehcleanup168

ehcleanup168:                                     ; preds = %ehcleanup164, %if.then.i.i289, %if.then.i.i.i291
  %.pn214.pn = phi { ptr, i32 } [ %.pn214, %ehcleanup164 ], [ %86, %if.then.i.i.i291 ], [ %86, %if.then.i.i289 ]
  call void @_ZNSt13unordered_mapINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmSt4hashIS5_ESt8equal_toIS5_ESaISt4pairIKS5_mEEED2Ev(ptr noundef nonnull align 8 dereferenceable(56) %frequencies) #20
  call void @llvm.lifetime.end.p0(i64 56, ptr nonnull %frequencies) #20
  br label %ehcleanup172

ehcleanup172:                                     ; preds = %ehcleanup168, %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit277
  %.pn215.pn = phi { ptr, i32 } [ %.pn215, %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEED2Ev.exit277 ], [ %.pn214.pn, %ehcleanup168 ]
  call void @_ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EED2Ev(ptr noundef nonnull align 8 dereferenceable(24) %normalized_ignore) #20
  call void @llvm.lifetime.end.p0(i64 24, ptr nonnull %normalized_ignore) #20
  %140 = load ptr, ptr %text, align 8, !tbaa !13
  %cmp.i.i.i363 = icmp eq ptr %140, %26
  br i1 %cmp.i.i.i363, label %if.then.i.i.i367, label %if.then.i.i364

if.then.i.i.i367:                                 ; preds = %ehcleanup172
  %141 = load i64, ptr %_M_string_length.i.i.i88.i, align 8, !tbaa !16
  %cmp3.i.i.i369 = icmp ult i64 %141, 16
  call void @llvm.assume(i1 %cmp3.i.i.i369)
  br label %ehcleanup178

if.then.i.i364:                                   ; preds = %ehcleanup172
  %142 = load i64, ptr %26, align 8, !tbaa !15
  %add.i.i.i365 = add i64 %142, 1
  call void @_ZdlPvm(ptr noundef %140, i64 noundef %add.i.i.i365) #23
  br label %ehcleanup178

ehcleanup178:                                     ; preds = %if.then.i.i364, %if.then.i.i.i367, %ehcleanup
  %.pn215.pn.pn = phi { ptr, i32 } [ %.pn, %ehcleanup ], [ %.pn215.pn, %if.then.i.i.i367 ], [ %.pn215.pn, %if.then.i.i364 ]
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %text) #20
  br label %ehcleanup180

ehcleanup180:                                     ; preds = %ehcleanup178, %lpad10, %lpad
  %.pn216 = phi { ptr, i32 } [ %9, %lpad10 ], [ %.pn215.pn.pn, %ehcleanup178 ], [ %4, %lpad ]
  %exn.slot.7 = extractvalue { ptr, i32 } %.pn216, 0
  call void @_ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EED2Ev(ptr noundef nonnull align 8 dereferenceable(24) %ignore) #20
  call void @llvm.lifetime.end.p0(i64 24, ptr nonnull %ignore) #20
  %143 = call ptr @__cxa_begin_catch(ptr %exn.slot.7) #20
  call void @__cxa_end_catch()
  br label %return

return:                                           ; preds = %ehcleanup180, %_ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EED2Ev.exit362, %lor.lhs.false, %if.end
  %retval.2 = phi ptr [ null, %ehcleanup180 ], [ %retval.1, %_ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EED2Ev.exit362 ], [ null, %lor.lhs.false ], [ null, %if.end ]
  ret ptr %retval.2
}

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #1

; Function Attrs: mustprogress uwtable
declare void @_ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EE7reserveEm(ptr noundef nonnull align 8 dereferenceable(24), i64 noundef) local_unnamed_addr #0 align 2

declare i32 @__gxx_personality_v0(...)

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #1

; Function Attrs: mustprogress uwtable
declare void @_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEC2IS3_EEPKcRKS3_(ptr noundef nonnull align 8 dereferenceable(32), ptr noundef, ptr noundef nonnull align 1 dereferenceable(1)) unnamed_addr #0 align 2

; Function Attrs: mustprogress uwtable
declare void @_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE7reserveEm(ptr noundef nonnull align 8 dereferenceable(32), i64 noundef) local_unnamed_addr #0 align 2

declare noundef zeroext i1 @_Z12is_word_charc(i8 noundef signext) local_unnamed_addr #2

declare noundef signext i8 @_Z14normalize_charc(i8 noundef signext) local_unnamed_addr #2

; Function Attrs: mustprogress uwtable
declare hidden fastcc void @_ZL24scan_text_tail_recursiveRKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmS4_RSt13unordered_mapIS4_mSt4hashIS4_ESt8equal_toIS4_ESaISt4pairIS5_mEEERKSt6vectorIS4_SaIS4_EE(ptr noundef nonnull align 8 dereferenceable(32), i64 noundef, ptr noundef nonnull, ptr noundef nonnull align 8 dereferenceable(56), ptr noundef nonnull align 8 dereferenceable(24)) unnamed_addr #0

; Function Attrs: mustprogress uwtable
declare void @_ZNSt6vectorISt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmESaIS7_EE7reserveEm(ptr noundef nonnull align 8 dereferenceable(24), i64 noundef) local_unnamed_addr #0 align 2

; Function Attrs: mustprogress uwtable
declare noundef nonnull align 8 dereferenceable(40) ptr @_ZNSt6vectorISt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmESaIS7_EE12emplace_backIJRKS6_RKmEEERS7_DpOT_(ptr noundef nonnull align 8 dereferenceable(24), ptr noundef nonnull align 8 dereferenceable(32), ptr noundef nonnull align 8 dereferenceable(8)) local_unnamed_addr #0 align 2

; Function Attrs: mustprogress nofree nounwind willreturn allockind("alloc,zeroed") allocsize(0,1) memory(inaccessiblemem: readwrite)
declare noalias noundef ptr @calloc(i64 noundef, i64 noundef) local_unnamed_addr #3

; Function Attrs: mustprogress uwtable
declare hidden fastcc void @_ZL23find_top_tail_recursiveN9__gnu_cxx17__normal_iteratorIPKSt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmESt6vectorIS8_SaIS8_EEEESE_P9WordCountm(ptr, ptr, ptr noundef nonnull, i64 noundef range(i64 1, 0)) unnamed_addr #0

; Function Attrs: mustprogress nounwind uwtable
declare hidden fastcc void @"_ZNSt10unique_ptrI9WordCountKZ19top_words_from_fileE3$_0ED2Ev"(ptr nocapture noundef nonnull align 8 dereferenceable(16)) unnamed_addr #4 align 2

; Function Attrs: mustprogress nounwind uwtable
declare void @_ZNSt6vectorISt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmESaIS7_EED2Ev(ptr noundef nonnull align 8 dereferenceable(24)) unnamed_addr #4 align 2

; Function Attrs: inlinehint mustprogress nounwind uwtable
declare void @_ZNSt13unordered_mapINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmSt4hashIS5_ESt8equal_toIS5_ESaISt4pairIKS5_mEEED2Ev(ptr noundef nonnull align 8 dereferenceable(56)) unnamed_addr #5 align 2

; Function Attrs: mustprogress nounwind uwtable
declare void @_ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EED2Ev(ptr noundef nonnull align 8 dereferenceable(24)) unnamed_addr #4 align 2

declare ptr @__cxa_begin_catch(ptr) local_unnamed_addr

declare void @__cxa_end_catch() local_unnamed_addr

; Function Attrs: cold noreturn
declare void @_ZSt20__throw_length_errorPKc(ptr noundef) local_unnamed_addr #6

; Function Attrs: noreturn
declare void @_ZSt17__throw_bad_allocv() local_unnamed_addr #7

; Function Attrs: nobuiltin allocsize(0)
declare noundef nonnull ptr @_Znwm(i64 noundef) local_unnamed_addr #8

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #9

; Function Attrs: nobuiltin nounwind
declare void @_ZdlPvm(ptr noundef, i64 noundef) local_unnamed_addr #10

; Function Attrs: mustprogress uwtable
declare void @_ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EE17_M_realloc_appendIJRKPKcEEEvDpOT_(ptr noundef nonnull align 8 dereferenceable(24), ptr noundef nonnull align 8 dereferenceable(8)) local_unnamed_addr #0 align 2

; Function Attrs: mustprogress uwtable
declare void @_ZNSt14basic_ifstreamIcSt11char_traitsIcEEC1ERKNSt7__cxx1112basic_stringIcS1_SaIcEEESt13_Ios_Openmode(ptr noundef nonnull align 8 dereferenceable(256), ptr noundef nonnull align 8 dereferenceable(32), i32 noundef) unnamed_addr #0 align 2

declare ptr @__cxa_allocate_exception(i64) local_unnamed_addr

; Function Attrs: inlinehint mustprogress uwtable
declare void @_ZStplIcSt11char_traitsIcESaIcEENSt7__cxx1112basic_stringIT_T0_T1_EEPKS5_RKS8_(ptr dead_on_unwind noalias writable sret(%"class.std::__cxx11::basic_string") align 8, ptr noundef, ptr noundef nonnull align 8 dereferenceable(32)) local_unnamed_addr #11

declare void @_ZNSt13runtime_errorC1ERKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE(ptr noundef nonnull align 8 dereferenceable(16), ptr noundef nonnull align 8 dereferenceable(32)) unnamed_addr #2

; Function Attrs: nounwind
declare void @_ZNSt13runtime_errorD1Ev(ptr noundef nonnull align 8 dereferenceable(16)) unnamed_addr #12

; Function Attrs: cold noreturn
declare void @__cxa_throw(ptr, ptr, ptr) local_unnamed_addr #13

declare void @__cxa_free_exception(ptr) local_unnamed_addr

declare noundef nonnull align 8 dereferenceable(16) ptr @_ZNSi5seekgElSt12_Ios_Seekdir(ptr noundef nonnull align 8 dereferenceable(16), i64 noundef, i32 noundef) local_unnamed_addr #2

declare { i64, i64 } @_ZNSi5tellgEv(ptr noundef nonnull align 8 dereferenceable(16)) local_unnamed_addr #2

declare noundef nonnull align 8 dereferenceable(16) ptr @_ZNSi4readEPcl(ptr noundef nonnull align 8 dereferenceable(16), ptr noundef, i64 noundef) local_unnamed_addr #2

; Function Attrs: nounwind
declare void @_ZNSt8ios_baseD2Ev(ptr noundef nonnull align 8 dereferenceable(216)) unnamed_addr #12

; Function Attrs: mustprogress uwtable
declare void @_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_mutateEmmPKcm(ptr noundef nonnull align 8 dereferenceable(32), i64 noundef, i64 noundef, ptr noundef, i64 noundef) local_unnamed_addr #0 align 2

; Function Attrs: mustprogress nofree nounwind willreturn memory(argmem: read)
declare i64 @strlen(ptr nocapture noundef) local_unnamed_addr #14

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: write)
declare void @llvm.memset.p0.i64(ptr nocapture writeonly, i8, i64, i1 immarg) #15

; Function Attrs: mustprogress nounwind uwtable
declare void @_ZNSt14basic_ifstreamIcSt11char_traitsIcEED2Ev(ptr noundef nonnull align 8 dereferenceable(256), ptr noundef) unnamed_addr #4 align 2

; Function Attrs: mustprogress uwtable
declare void @_ZNSt6vectorINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EE17_M_realloc_appendIJS5_EEEvDpOT_(ptr noundef nonnull align 8 dereferenceable(24), ptr noundef nonnull align 8 dereferenceable(32)) local_unnamed_addr #0 align 2

declare noundef ptr @_Z16copy_to_c_stringRKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE(ptr noundef nonnull align 8 dereferenceable(32)) local_unnamed_addr #2

; Function Attrs: nounwind
declare void @_ZNSt9bad_allocD1Ev(ptr noundef nonnull align 8 dereferenceable(8)) unnamed_addr #12

; Function Attrs: mustprogress nounwind willreturn allockind("free") memory(argmem: readwrite, inaccessiblemem: readwrite)
declare void @free(ptr allocptr nocapture noundef) local_unnamed_addr #16

; Function Attrs: mustprogress nofree nounwind willreturn memory(argmem: read)
declare i32 @strcmp(ptr nocapture noundef, ptr nocapture noundef) local_unnamed_addr #14

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: write)
declare void @llvm.assume(i1 noundef) #17

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: readwrite)
declare void @llvm.experimental.noalias.scope.decl(metadata) #18

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i64 @llvm.umin.i64(i64, i64) #19

attributes #0 = { mustprogress uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { mustprogress nofree nounwind willreturn allockind("alloc,zeroed") allocsize(0,1) memory(inaccessiblemem: readwrite) "alloc-family"="malloc" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { mustprogress nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { inlinehint mustprogress nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #6 = { cold noreturn "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #7 = { noreturn "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #8 = { nobuiltin allocsize(0) "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #9 = { nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #10 = { nobuiltin nounwind "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #11 = { inlinehint mustprogress uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #12 = { nounwind "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #13 = { cold noreturn }
attributes #14 = { mustprogress nofree nounwind willreturn memory(argmem: read) "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #15 = { nocallback nofree nounwind willreturn memory(argmem: write) }
attributes #16 = { mustprogress nounwind willreturn allockind("free") memory(argmem: readwrite, inaccessiblemem: readwrite) "alloc-family"="malloc" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #17 = { nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: write) }
attributes #18 = { nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: readwrite) }
attributes #19 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #20 = { nounwind }
attributes #21 = { noreturn }
attributes #22 = { builtin allocsize(0) }
attributes #23 = { builtin nounwind }
attributes #24 = { nounwind allocsize(0,1) }
attributes #25 = { nounwind willreturn memory(read) }

!llvm.linker.options = !{}
!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"uwtable", i32 2}
!3 = !{!"clang version 20.1.8 (CentOS 20.1.8-9.el10_2)"}
!4 = !{!5, !5, i64 0}
!5 = !{!"long", !6, i64 0}
!6 = !{!"omnipotent char", !7, i64 0}
!7 = !{!"Simple C++ TBAA"}
!8 = !{!9, !10, i64 0}
!9 = !{!"_ZTSNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE12_Alloc_hiderE", !10, i64 0}
!10 = !{!"p1 omnipotent char", !11, i64 0}
!11 = !{!"any pointer", !6, i64 0}
!12 = !{!"branch_weights", !"expected", i32 1, i32 2000}
!13 = !{!14, !10, i64 0}
!14 = !{!"_ZTSNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE", !9, i64 0, !5, i64 8, !6, i64 16}
!15 = !{!6, !6, i64 0}
!16 = !{!14, !5, i64 8}
!17 = !{!18}
!18 = distinct !{!18, !19, !"_ZL15read_whole_fileRKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE: %agg.result"}
!19 = distinct !{!19, !"_ZL15read_whole_fileRKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE"}
!20 = !{!10, !10, i64 0}
!21 = !{!22, !23, i64 8}
!22 = !{!"_ZTSNSt12_Vector_baseINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESaIS5_EE17_Vector_impl_dataE", !23, i64 0, !23, i64 8, !23, i64 16}
!23 = !{!"p1 _ZTSNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE", !11, i64 0}
!24 = !{!22, !23, i64 16}
!25 = distinct !{!25, !26, !27}
!26 = !{!"llvm.loop.mustprogress"}
!27 = !{!"llvm.loop.unroll.disable"}
!28 = !{!29, !29, i64 0}
!29 = !{!"vtable pointer", !7, i64 0}
!30 = !{!31, !33, i64 32}
!31 = !{!"_ZTSSt8ios_base", !5, i64 8, !5, i64 16, !32, i64 24, !33, i64 28, !33, i64 32, !34, i64 40, !35, i64 48, !6, i64 64, !36, i64 192, !37, i64 200, !38, i64 208}
!32 = !{!"_ZTSSt13_Ios_Fmtflags", !6, i64 0}
!33 = !{!"_ZTSSt12_Ios_Iostate", !6, i64 0}
!34 = !{!"p1 _ZTSNSt8ios_base14_Callback_listE", !11, i64 0}
!35 = !{!"_ZTSNSt8ios_base6_WordsE", !11, i64 0, !5, i64 8}
!36 = !{!"int", !6, i64 0}
!37 = !{!"p1 _ZTSNSt8ios_base6_WordsE", !11, i64 0}
!38 = !{!"_ZTSSt6locale", !39, i64 0}
!39 = !{!"p1 _ZTSNSt6locale5_ImplE", !11, i64 0}
!40 = !{!23, !23, i64 0}
!41 = !{!42, !43, i64 0}
!42 = !{!"_ZTSSt10_HashtableINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEESt4pairIKS5_mESaIS8_ENSt8__detail10_Select1stESt8equal_toIS5_ESt4hashIS5_ENSA_18_Mod_range_hashingENSA_20_Default_ranged_hashENSA_20_Prime_rehash_policyENSA_17_Hashtable_traitsILb1ELb0ELb1EEEE", !43, i64 0, !5, i64 8, !44, i64 16, !5, i64 24, !46, i64 32, !45, i64 48}
!43 = !{!"p2 _ZTSNSt8__detail15_Hash_node_baseE", !11, i64 0}
!44 = !{!"_ZTSNSt8__detail15_Hash_node_baseE", !45, i64 0}
!45 = !{!"p1 _ZTSNSt8__detail15_Hash_node_baseE", !11, i64 0}
!46 = !{!"_ZTSNSt8__detail20_Prime_rehash_policyE", !47, i64 0, !5, i64 8}
!47 = !{!"float", !6, i64 0}
!48 = !{!42, !5, i64 8}
!49 = !{!46, !47, i64 0}
!50 = distinct !{!50, !27}
!51 = distinct !{!51, !27}
!52 = !{!42, !5, i64 24}
!53 = !{!42, !45, i64 16}
!54 = !{!55, !56, i64 8}
!55 = !{!"_ZTSNSt12_Vector_baseISt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmESaIS7_EE17_Vector_impl_dataE", !56, i64 0, !56, i64 8, !56, i64 16}
!56 = !{!"p1 _ZTSSt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmE", !11, i64 0}
!57 = !{!55, !56, i64 0}
!58 = !{!44, !45, i64 0}
!59 = distinct !{!59, !27}
!60 = !{!61, !62, i64 0}
!61 = !{!"_ZTSSt10_Head_baseILm0EP9WordCountLb0EE", !62, i64 0}
!62 = !{!"p1 _ZTS9WordCount", !11, i64 0}
!63 = !{!56, !56, i64 0}
!64 = !{!65, !5, i64 32}
!65 = !{!"_ZTSSt4pairINSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEEmE", !14, i64 0, !5, i64 32}
!66 = !{!67, !5, i64 8}
!67 = !{!"_ZTS9WordCount", !10, i64 0, !5, i64 8}
!68 = !{!67, !10, i64 0}
!69 = distinct !{!69, !26, !27}
!70 = !{i64 0, i64 8, !20, i64 8, i64 8, !4}
!71 = distinct !{!71, !26, !27}
!72 = distinct !{!72, !26, !27}
!73 = !{!62, !62, i64 0}
!74 = distinct !{!74, !26, !27}
!75 = !{!55, !56, i64 16}
!76 = distinct !{!76, !26, !27}
!77 = !{!22, !23, i64 0}
!78 = distinct !{!78, !26, !27}
