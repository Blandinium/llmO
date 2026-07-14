; ModuleID = '/home/tijl/code/llmO/SUT/format_list.cpp'
source_filename = "/home/tijl/code/llmO/SUT/format_list.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-redhat-linux-gnu"

%"class.std::__cxx11::basic_string" = type { %"struct.std::__cxx11::basic_string<char>::_Alloc_hider", i64, %union.anon }
%"struct.std::__cxx11::basic_string<char>::_Alloc_hider" = type { ptr }
%union.anon = type { i64, [8 x i8] }

$__clang_call_terminate = comdat any

$_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_mutateEmmPKcm = comdat any

$_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE7reserveEm = comdat any

@.str.1 = private unnamed_addr constant [3 x i8] c", \00", align 1
@.str.2 = private unnamed_addr constant [2 x i8] c"]\00", align 1
@.str.4 = private unnamed_addr constant [24 x i8] c"basic_string::_M_create\00", align 1
@.str.5 = private unnamed_addr constant [21 x i8] c"basic_string::append\00", align 1
@__const._ZNSt8__detail18__to_chars_10_implIjEEvPcjT_.__digits = private unnamed_addr constant [201 x i8] c"00010203040506070809101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899\00", align 16

; Function Attrs: mustprogress uwtable
define noundef ptr @format_list(ptr noundef readonly %input, i64 noundef %input_length) local_unnamed_addr #0 personality ptr @__gxx_personality_v0 {
entry:
  %result = alloca %"class.std::__cxx11::basic_string", align 8
  %cmp = icmp eq ptr %input, null
  %cmp1 = icmp ne i64 %input_length, 0
  %or.cond = and i1 %cmp, %cmp1
  br i1 %or.cond, label %return_null, label %init

return_null:                                      ; preds = %entry
  ret ptr null

init:                                             ; preds = %entry
  call void @llvm.lifetime.start.p0(i64 32, ptr nonnull %result) #13
  %mul = mul i64 %input_length, 13
  %max_len = add i64 %mul, 2
  %is_heap = icmp ugt i64 %max_len, 15
  br i1 %is_heap, label %alloc_heap, label %alloc_sso

alloc_heap:                                       ; preds = %init
  %alloc_sz = add i64 %max_len, 1
  %heap_ptr = invoke ptr @_Znwm(i64 %alloc_sz) #18
          to label %alloc_done unwind label %lpad_alloc

alloc_sso:                                        ; preds = %init
  %sso_ptr = getelementptr inbounds nuw i8, ptr %result, i64 16
  br label %alloc_done

alloc_done:                                       ; preds = %alloc_sso, %alloc_heap
  %buf = phi ptr [ %heap_ptr, %alloc_heap ], [ %sso_ptr, %alloc_sso ]
  %cap = phi i64 [ %max_len, %alloc_heap ], [ 15, %alloc_sso ]
  store ptr %buf, ptr %result, align 8
  br i1 %is_heap, label %set_cap_heap, label %set_cap_done

set_cap_heap:                                     ; preds = %alloc_done
  %cap_ptr = getelementptr inbounds nuw i8, ptr %result, i64 16
  store i64 %cap, ptr %cap_ptr, align 8
  br label %set_cap_done

set_cap_done:                                     ; preds = %set_cap_heap, %alloc_done
  store i8 91, ptr %buf, align 1
  %cmp_len = icmp eq i64 %input_length, 0
  br i1 %cmp_len, label %loop_end, label %loop_header

loop_header:                                      ; preds = %set_cap_done
  br label %loop_body

loop_body:                                        ; preds = %loop_header, %loop_continue
  %i = phi i64 [ 0, %loop_header ], [ %i_next, %loop_continue ]
  %pos = phi i64 [ 1, %loop_header ], [ %pos_next, %loop_continue ]
  %needs_comma = icmp ugt i64 %i, 0
  br i1 %needs_comma, label %write_comma, label %read_val

write_comma:                                      ; preds = %loop_body
  %ptr_comma1 = getelementptr inbounds i8, ptr %buf, i64 %pos
  store i8 44, ptr %ptr_comma1, align 1
  %pos_plus1 = add i64 %pos, 1
  %ptr_comma2 = getelementptr inbounds i8, ptr %buf, i64 %pos_plus1
  store i8 32, ptr %ptr_comma2, align 1
  %pos_after_comma = add i64 %pos, 2
  br label %read_val

read_val:                                         ; preds = %write_comma, %loop_body
  %pos_curr = phi i64 [ %pos, %loop_body ], [ %pos_after_comma, %write_comma ]
  %input_ptr = getelementptr inbounds i32, ptr %input, i64 %i
  %val = load i32, ptr %input_ptr, align 4
  %is_zero = icmp eq i32 %val, 0
  br i1 %is_zero, label %val_zero, label %val_nonzero

val_zero:                                         ; preds = %read_val
  %ptr_zero = getelementptr inbounds i8, ptr %buf, i64 %pos_curr
  store i8 48, ptr %ptr_zero, align 1
  %pos_after_zero = add i64 %pos_curr, 1
  br label %loop_continue

val_nonzero:                                      ; preds = %read_val
  %is_neg = icmp slt i32 %val, 0
  br i1 %is_neg, label %val_neg, label %val_pos

val_neg:                                          ; preds = %val_nonzero
  %ptr_neg = getelementptr inbounds i8, ptr %buf, i64 %pos_curr
  store i8 45, ptr %ptr_neg, align 1
  %pos_after_neg = add i64 %pos_curr, 1
  %is_min = icmp eq i32 %val, -2147483648
  br i1 %is_min, label %val_min, label %val_neg_norm

val_min:                                          ; preds = %val_neg
  %ptr_min = getelementptr inbounds i8, ptr %buf, i64 %pos_after_neg
  store i64 3905531278153494834, ptr %ptr_min, align 1
  %ptr_min8 = getelementptr inbounds i8, ptr %ptr_min, i64 8
  store i16 14388, ptr %ptr_min8, align 1
  %pos_after_min = add i64 %pos_after_neg, 10
  br label %loop_continue

val_neg_norm:                                     ; preds = %val_neg
  %val_abs = sub i32 0, %val
  br label %val_pos

val_pos:                                          ; preds = %val_neg_norm, %val_nonzero
  %pos_w = phi i64 [ %pos_curr, %val_nonzero ], [ %pos_after_neg, %val_neg_norm ]
  %val_w = phi i32 [ %val, %val_nonzero ], [ %val_abs, %val_neg_norm ]
  br label %count_digits

count_digits:                                     ; preds = %count_digits, %val_pos
  %temp = phi i32 [ %val_w, %val_pos ], [ %temp_next, %count_digits ]
  %digits = phi i64 [ 0, %val_pos ], [ %digits_next, %count_digits ]
  %temp_next = udiv i32 %temp, 10
  %digits_next = add i64 %digits, 1
  %cmp_count = icmp ugt i32 %temp_next, 0
  br i1 %cmp_count, label %count_digits, label %count_done

count_done:                                       ; preds = %count_digits
  %pos_end = add i64 %pos_w, %digits
  br label %write_digits

write_digits:                                     ; preds = %write_digits, %count_done
  %val_wd = phi i32 [ %val_w, %count_done ], [ %val_wd_next, %write_digits ]
  %p2 = phi i64 [ %pos_end, %count_done ], [ %p2_next, %write_digits ]
  %p2_next = sub i64 %p2, 1
  %rem = urem i32 %val_wd, 10
  %val_wd_next = udiv i32 %val_wd, 10
  %char = trunc i32 %rem to i8
  %char_ascii = add i8 %char, 48
  %ptr_w = getelementptr inbounds i8, ptr %buf, i64 %p2_next
  store i8 %char_ascii, ptr %ptr_w, align 1
  %cmp_wd = icmp ugt i32 %val_wd_next, 0
  br i1 %cmp_wd, label %write_digits, label %write_done

write_done:                                       ; preds = %write_digits
  br label %loop_continue

loop_continue:                                    ; preds = %write_done, %val_min, %val_zero
  %pos_next = phi i64 [ %pos_after_zero, %val_zero ], [ %pos_after_min, %val_min ], [ %pos_end, %write_done ]
  %i_next = add i64 %i, 1
  %cmp_loop = icmp eq i64 %i_next, %input_length
  br i1 %cmp_loop, label %loop_end, label %loop_body

loop_end:                                         ; preds = %loop_continue, %set_cap_done
  %pos_final = phi i64 [ 1, %set_cap_done ], [ %pos_next, %loop_continue ]
  %ptr_close = getelementptr inbounds i8, ptr %buf, i64 %pos_final
  store i8 93, ptr %ptr_close, align 1
  %pos_total = add i64 %pos_final, 1
  %ptr_null = getelementptr inbounds i8, ptr %buf, i64 %pos_total
  store i8 0, ptr %ptr_null, align 1
  %len_ptr = getelementptr inbounds nuw i8, ptr %result, i64 8
  store i64 %pos_total, ptr %len_ptr, align 8
  %ret_c_str = invoke noundef ptr @_Z16copy_to_c_stringRKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE(ptr noundef nonnull align 8 dereferenceable(32) %result)
          to label %invoke_cont unwind label %lpad

invoke_cont:                                      ; preds = %loop_end
  br i1 %is_heap, label %free_heap, label %free_done

free_heap:                                        ; preds = %invoke_cont
  %alloc_sz_free = add i64 %max_len, 1
  call void @_ZdlPvm(ptr noundef %heap_ptr, i64 noundef %alloc_sz_free) #16
  br label %free_done

free_done:                                        ; preds = %free_heap, %invoke_cont
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %result) #13
  ret ptr %ret_c_str

lpad_alloc:                                       ; preds = %alloc_heap
  %lp_alloc = landingpad { ptr, i32 }
          catch ptr null
  br label %catch_block

lpad:                                             ; preds = %loop_end
  %lp = landingpad { ptr, i32 }
          catch ptr null
  br i1 %is_heap, label %lpad_free, label %catch_block

lpad_free:                                        ; preds = %lpad
  %alloc_sz_lp = add i64 %max_len, 1
  call void @_ZdlPvm(ptr noundef %heap_ptr, i64 noundef %alloc_sz_lp) #16
  br label %catch_block

catch_block:                                      ; preds = %lpad_free, %lpad, %lpad_alloc
  %exn_val = phi { ptr, i32 } [ %lp_alloc, %lpad_alloc ], [ %lp, %lpad ], [ %lp, %lpad_free ]
  %exn = extractvalue { ptr, i32 } %exn_val, 0
  call void @llvm.lifetime.end.p0(i64 32, ptr nonnull %result) #13
  %catch_ptr = call ptr @__cxa_begin_catch(ptr %exn) #13
  call void @__cxa_end_catch()
  ret ptr null
}

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.start.p0(i64 immarg, ptr nocapture) #1

declare i32 @__gxx_personality_v0(...)

; Function Attrs: mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite)
declare void @llvm.lifetime.end.p0(i64 immarg, ptr nocapture) #1

declare noundef ptr @_Z16copy_to_c_stringRKNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE(ptr noundef nonnull align 8 dereferenceable(32)) local_unnamed_addr #2

declare ptr @__cxa_begin_catch(ptr) local_unnamed_addr

declare void @__cxa_end_catch() local_unnamed_addr

; Function Attrs: cold noreturn
declare void @_ZSt20__throw_length_errorPKc(ptr noundef) local_unnamed_addr #3

; Function Attrs: noinline noreturn nounwind uwtable
define linkonce_odr hidden void @__clang_call_terminate(ptr noundef %0) local_unnamed_addr #4 comdat {
  %2 = tail call ptr @__cxa_begin_catch(ptr %0) #13
  tail call void @_ZSt9terminatev() #15
  unreachable
}

; Function Attrs: cold nofree noreturn
declare void @_ZSt9terminatev() local_unnamed_addr #5

; Function Attrs: noreturn
declare void @_ZSt17__throw_bad_allocv() local_unnamed_addr #6

; Function Attrs: nobuiltin allocsize(0)
declare noundef nonnull ptr @_Znwm(i64 noundef) local_unnamed_addr #7

; Function Attrs: mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite)
declare void @llvm.memcpy.p0.p0.i64(ptr noalias nocapture writeonly, ptr noalias nocapture readonly, i64, i1 immarg) #8

; Function Attrs: nobuiltin nounwind
declare void @_ZdlPvm(ptr noundef, i64 noundef) local_unnamed_addr #9

; Function Attrs: mustprogress uwtable
define linkonce_odr void @_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_mutateEmmPKcm(ptr noundef nonnull align 8 dereferenceable(32) %this, i64 noundef %__pos, i64 noundef %__len1, ptr noundef %__s, i64 noundef %__len2) local_unnamed_addr #0 comdat align 2 personality ptr @__gxx_personality_v0 {
entry:
  %_M_string_length.i = getelementptr inbounds nuw i8, ptr %this, i64 8
  %0 = load i64, ptr %_M_string_length.i, align 8, !tbaa !11
  %1 = add i64 %__len1, %__pos
  %sub2 = sub i64 %0, %1
  %add = sub i64 %__len2, %__len1
  %sub4 = add i64 %add, %0
  %2 = load ptr, ptr %this, align 8, !tbaa !14
  %3 = getelementptr inbounds nuw i8, ptr %this, i64 16
  %cmp.i.i = icmp eq ptr %2, %3
  br i1 %cmp.i.i, label %if.then.i.i, label %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit

if.then.i.i:                                      ; preds = %entry
  %cmp3.i.i = icmp ult i64 %0, 16
  tail call void @llvm.assume(i1 %cmp3.i.i)
  br label %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit

_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit: ; preds = %entry, %if.then.i.i
  %4 = load i64, ptr %3, align 8
  %cond.i = select i1 %cmp.i.i, i64 15, i64 %4
  %cmp.i = icmp slt i64 %sub4, 0
  br i1 %cmp.i, label %if.then.i, label %if.end.i

if.then.i:                                        ; preds = %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit
  tail call void @_ZSt20__throw_length_errorPKc(ptr noundef nonnull @.str.4) #14
  unreachable

if.end.i:                                         ; preds = %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit
  %cmp2.i = icmp ugt i64 %sub4, %cond.i
  br i1 %cmp2.i, label %land.lhs.true.i, label %if.end11.i

land.lhs.true.i:                                  ; preds = %if.end.i
  %mul.i = shl i64 %cond.i, 1
  %cmp3.i = icmp ult i64 %sub4, %mul.i
  br i1 %cmp3.i, label %if.then4.i, label %if.end11.i

if.then4.i:                                       ; preds = %land.lhs.true.i
  %spec.store.select.i = tail call i64 @llvm.umin.i64(i64 %mul.i, i64 9223372036854775807)
  br label %if.end11.i

if.end11.i:                                       ; preds = %if.then4.i, %land.lhs.true.i, %if.end.i
  %__new_capacity.0 = phi i64 [ %spec.store.select.i, %if.then4.i ], [ %sub4, %land.lhs.true.i ], [ %sub4, %if.end.i ]
  %add.i = add nuw i64 %__new_capacity.0, 1
  %cmp.i.i.i = icmp slt i64 %add.i, 0
  br i1 %cmp.i.i.i, label %if.end.i.i.i, label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm.exit, !prof !25

if.end.i.i.i:                                     ; preds = %if.end11.i
  tail call void @_ZSt17__throw_bad_allocv() #17
  unreachable

_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm.exit: ; preds = %if.end11.i
  %call5.i.i.i = tail call noalias noundef nonnull ptr @_Znwm(i64 noundef %add.i) #18
  switch i64 %__pos, label %if.end.i.i [
    i64 0, label %if.end
    i64 1, label %if.then.i37
  ]

if.then.i37:                                      ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm.exit
  %5 = load i8, ptr %2, align 1, !tbaa !10
  store i8 %5, ptr %call5.i.i.i, align 1, !tbaa !10
  br label %if.end

if.end.i.i:                                       ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm.exit
  tail call void @llvm.memcpy.p0.p0.i64(ptr nonnull align 1 %call5.i.i.i, ptr align 1 %2, i64 %__pos, i1 false)
  br label %if.end

if.end:                                           ; preds = %if.end.i.i, %if.then.i37, %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm.exit
  %tobool8 = icmp ne ptr %__s, null
  %tobool9 = icmp ne i64 %__len2, 0
  %or.cond = and i1 %tobool8, %tobool9
  br i1 %or.cond, label %if.then10, label %if.end11

if.then10:                                        ; preds = %if.end
  %add.ptr = getelementptr inbounds nuw i8, ptr %call5.i.i.i, i64 %__pos
  switch i64 %__len2, label %if.end.i.i40 [
    i64 1, label %if.then.i39
    i64 0, label %if.end11
  ]

if.then.i39:                                      ; preds = %if.then10
  %6 = load i8, ptr %__s, align 1, !tbaa !10
  store i8 %6, ptr %add.ptr, align 1, !tbaa !10
  br label %if.end11

if.end.i.i40:                                     ; preds = %if.then10
  tail call void @llvm.memcpy.p0.p0.i64(ptr nonnull align 1 %add.ptr, ptr nonnull align 1 %__s, i64 %__len2, i1 false)
  br label %if.end11

if.end11:                                         ; preds = %if.end.i.i40, %if.then.i39, %if.then10, %if.end
  %tobool12.not = icmp eq i64 %0, %1
  br i1 %tobool12.not, label %if.end19, label %if.then13

if.then13:                                        ; preds = %if.end11
  %add.ptr14 = getelementptr inbounds nuw i8, ptr %call5.i.i.i, i64 %__pos
  %add.ptr15 = getelementptr inbounds nuw i8, ptr %add.ptr14, i64 %__len2
  %add.ptr17 = getelementptr inbounds nuw i8, ptr %2, i64 %__pos
  %add.ptr18 = getelementptr inbounds nuw i8, ptr %add.ptr17, i64 %__len1
  switch i64 %sub2, label %if.end.i.i44 [
    i64 1, label %if.then.i43
    i64 0, label %if.end19
  ]

if.then.i43:                                      ; preds = %if.then13
  %7 = load i8, ptr %add.ptr18, align 1, !tbaa !10
  store i8 %7, ptr %add.ptr15, align 1, !tbaa !10
  br label %if.end19

if.end.i.i44:                                     ; preds = %if.then13
  tail call void @llvm.memcpy.p0.p0.i64(ptr nonnull align 1 %add.ptr15, ptr align 1 %add.ptr18, i64 %sub2, i1 false)
  br label %if.end19

if.end19:                                         ; preds = %if.end.i.i44, %if.then.i43, %if.then13, %if.end11
  br i1 %cmp.i.i, label %if.then.i.i49, label %if.then.i47

if.then.i.i49:                                    ; preds = %if.end19
  %cmp3.i.i51 = icmp ult i64 %0, 16
  tail call void @llvm.assume(i1 %cmp3.i.i51)
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_disposeEv.exit

if.then.i47:                                      ; preds = %if.end19
  %add.i.i = add i64 %4, 1
  tail call void @_ZdlPvm(ptr noundef %2, i64 noundef %add.i.i) #16
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_disposeEv.exit

_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_disposeEv.exit: ; preds = %if.then.i.i49, %if.then.i47
  store ptr %call5.i.i.i, ptr %this, align 8, !tbaa !14
  store i64 %__new_capacity.0, ptr %3, align 8, !tbaa !10
  ret void
}

; Function Attrs: mustprogress uwtable
define linkonce_odr void @_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE7reserveEm(ptr noundef nonnull align 8 dereferenceable(32) %this, i64 noundef %__res) local_unnamed_addr #0 comdat align 2 personality ptr @__gxx_personality_v0 {
entry:
  %0 = load ptr, ptr %this, align 8, !tbaa !14
  %1 = getelementptr inbounds nuw i8, ptr %this, i64 16
  %cmp.i.i = icmp eq ptr %0, %1
  br i1 %cmp.i.i, label %if.then.i.i, label %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit

if.then.i.i:                                      ; preds = %entry
  %_M_string_length.i.i = getelementptr inbounds nuw i8, ptr %this, i64 8
  %2 = load i64, ptr %_M_string_length.i.i, align 8, !tbaa !11
  %cmp3.i.i = icmp ult i64 %2, 16
  tail call void @llvm.assume(i1 %cmp3.i.i)
  br label %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit

_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit: ; preds = %entry, %if.then.i.i
  %3 = load i64, ptr %1, align 8
  %cond.i = select i1 %cmp.i.i, i64 15, i64 %3
  %cmp.not = icmp ugt i64 %__res, %cond.i
  br i1 %cmp.not, label %if.end, label %cleanup

if.end:                                           ; preds = %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit
  %cmp.i = icmp slt i64 %__res, 0
  br i1 %cmp.i, label %if.then.i, label %land.lhs.true.i

if.then.i:                                        ; preds = %if.end
  tail call void @_ZSt20__throw_length_errorPKc(ptr noundef nonnull @.str.4) #14
  unreachable

land.lhs.true.i:                                  ; preds = %if.end
  %mul.i = shl i64 %cond.i, 1
  %cmp3.i = icmp ult i64 %__res, %mul.i
  %spec.store.select.i = tail call i64 @llvm.umin.i64(i64 %mul.i, i64 9223372036854775807)
  %__res.addr.0 = select i1 %cmp3.i, i64 %spec.store.select.i, i64 %__res
  %add.i = add nuw i64 %__res.addr.0, 1
  %cmp.i.i.i = icmp slt i64 %add.i, 0
  br i1 %cmp.i.i.i, label %if.end.i.i.i, label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm.exit, !prof !25

if.end.i.i.i:                                     ; preds = %land.lhs.true.i
  tail call void @_ZSt17__throw_bad_allocv() #17
  unreachable

_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm.exit: ; preds = %land.lhs.true.i
  %call5.i.i.i = tail call noalias noundef nonnull ptr @_Znwm(i64 noundef %add.i) #18
  %_M_string_length.i = getelementptr inbounds nuw i8, ptr %this, i64 8
  %4 = load i64, ptr %_M_string_length.i, align 8, !tbaa !11
  switch i64 %4, label %if.end.i.i [
    i64 0, label %if.then.i8
    i64 -1, label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE7_S_copyEPcPKcm.exit
  ]

if.then.i8:                                       ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm.exit
  %5 = load i8, ptr %0, align 1, !tbaa !10
  store i8 %5, ptr %call5.i.i.i, align 1, !tbaa !10
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE7_S_copyEPcPKcm.exit

if.end.i.i:                                       ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm.exit
  %add = add i64 %4, 1
  tail call void @llvm.memcpy.p0.p0.i64(ptr nonnull align 1 %call5.i.i.i, ptr align 1 %0, i64 %add, i1 false)
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE7_S_copyEPcPKcm.exit

_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE7_S_copyEPcPKcm.exit: ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE9_M_createERmm.exit, %if.then.i8, %if.end.i.i
  br i1 %cmp.i.i, label %if.then.i.i12, label %if.then.i10

if.then.i.i12:                                    ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE7_S_copyEPcPKcm.exit
  %cmp3.i.i14 = icmp ult i64 %4, 16
  tail call void @llvm.assume(i1 %cmp3.i.i14)
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_disposeEv.exit

if.then.i10:                                      ; preds = %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE7_S_copyEPcPKcm.exit
  %add.i.i = add i64 %3, 1
  tail call void @_ZdlPvm(ptr noundef %0, i64 noundef %add.i.i) #16
  br label %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_disposeEv.exit

_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_disposeEv.exit: ; preds = %if.then.i.i12, %if.then.i10
  store ptr %call5.i.i.i, ptr %this, align 8, !tbaa !14
  store i64 %__res.addr.0, ptr %1, align 8, !tbaa !10
  br label %cleanup

cleanup:                                          ; preds = %_ZNKSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE8capacityEv.exit, %_ZNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE10_M_disposeEv.exit
  ret void
}

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: write)
declare void @llvm.assume(i1 noundef) #10

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i32 @llvm.abs.i32(i32, i1 immarg) #11

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare i64 @llvm.umin.i64(i64, i64) #11

; Function Attrs: nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: readwrite)
declare void @llvm.experimental.noalias.scope.decl(metadata) #12

attributes #0 = { mustprogress uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { mustprogress nocallback nofree nosync nounwind willreturn memory(argmem: readwrite) }
attributes #2 = { "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #3 = { cold noreturn "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #4 = { noinline noreturn nounwind uwtable "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #5 = { cold nofree noreturn }
attributes #6 = { noreturn "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #7 = { nobuiltin allocsize(0) "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #8 = { mustprogress nocallback nofree nounwind willreturn memory(argmem: readwrite) }
attributes #9 = { nobuiltin nounwind "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #10 = { nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: write) }
attributes #11 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #12 = { nocallback nofree nosync nounwind willreturn memory(inaccessiblemem: readwrite) }
attributes #13 = { nounwind }
attributes #14 = { cold noreturn }
attributes #15 = { noreturn nounwind }
attributes #16 = { builtin nounwind }
attributes #17 = { noreturn }
attributes #18 = { builtin allocsize(0) }

!llvm.linker.options = !{}
!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 8, !"PIC Level", i32 2}
!2 = !{i32 7, !"uwtable", i32 2}
!3 = !{!"clang version 20.1.8 (CentOS 20.1.8-9.el10_2)"}
!4 = !{!5, !6, i64 0}
!5 = !{!"_ZTSNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEE12_Alloc_hiderE", !6, i64 0}
!6 = !{!"p1 omnipotent char", !7, i64 0}
!7 = !{!"any pointer", !8, i64 0}
!8 = !{!"omnipotent char", !9, i64 0}
!9 = !{!"Simple C++ TBAA"}
!10 = !{!8, !8, i64 0}
!11 = !{!12, !13, i64 8}
!12 = !{!"_ZTSNSt7__cxx1112basic_stringIcSt11char_traitsIcESaIcEEE", !5, i64 0, !13, i64 8, !8, i64 16}
!13 = !{!"long", !8, i64 0}
!14 = !{!12, !6, i64 0}
!15 = !{!16, !16, i64 0}
!16 = !{!"int", !8, i64 0}
!17 = !{!18}
!18 = distinct !{!18, !19, !"_ZNSt7__cxx119to_stringEi: %agg.result"}
!19 = distinct !{!19, !"_ZNSt7__cxx119to_stringEi"}
!20 = distinct !{!20, !21, !22}
!21 = !{!"llvm.loop.mustprogress"}
!22 = !{!"llvm.loop.unroll.disable"}
!23 = distinct !{!23, !21, !22}
!24 = distinct !{!24, !21, !22}
!25 = !{!"branch_weights", !"expected", i32 1, i32 2000}
