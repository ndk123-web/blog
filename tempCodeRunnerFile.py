@app.route('/delete/<string:sno>')
def delete(sno):
    
    req_post = Posts.query.filter_by(sno=sno).first()
    
    if not req_post:
        flash('Post not found','danger')
        return redirect(request.url)
    
    try:
        db.session.delete(req_post)
        db.session.commit()
        flash('successfully deleted post! ','success')
    except Exception as e:
        db.session.rollback()
        flash(f'Something messing: {e}','danger')
        return redirect(request.url)

    all_posts = Posts.query.filter_by().all()
    return render_template('admin_dashboard.html',params=params,posts=all_posts,time_ago_converter=time_ago_converter)