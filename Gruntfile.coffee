module.exports = (grunt) ->
  grunt.initConfig
    sass:
      dist:
        options:
          style: 'compressed'
          compass: true
        files: 'bikeme/apps/core/static/css/bikeme.css': 'bikeme/apps/core/static/sass/bikeme.sass'

    watch:
      options:
        livereload: true
      sass:
        options:
          livereload: false
        files: 'bikeme/apps/core/static/sass/*.s?ss'
        tasks: ["sass", ]
      css:
        files: 'bikeme/apps/core/static/css/*.css'
        tasks: []

  grunt.loadNpmTasks 'grunt-contrib-sass'
  grunt.loadNpmTasks 'grunt-contrib-watch'

  grunt.registerTask 'default', ['sass']
  grunt.registerTask 'dev', ['default', 'watch']
